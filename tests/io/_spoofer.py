# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

# pylint: disable=protected-access

import typing
import pytest
import logging
import asyncio
import pyuavcan
from pyuavcan.transport.loopback import LoopbackTransport, LoopbackCapture
from pyuavcan.presentation import Presentation
from yukon.io._spoofer import Spoofer, IfaceStatus
from org_uavcan_yukon.io.transfer import Spoof_0_1 as Spoof
import uavcan.node
import uavcan.node.port
import uavcan.si.unit.duration
import org_uavcan_yukon.io.transfer


@pytest.mark.asyncio
async def _unittest_spoofer(caplog: pytest.LogCaptureFixture) -> None:
    dcs_pres = Presentation(LoopbackTransport(1234))
    dcs_pub_spoof = dcs_pres.make_publisher(Spoof, 1)
    spoofer = Spoofer(dcs_pres.make_subscriber(Spoof, 1))

    # No target transports configured -- spoofing will do nothing except incrementing the transfer-ID counter.
    assert await dcs_pub_spoof.publish(
        Spoof(
            timeout=uavcan.si.unit.duration.Scalar_1_0(1.0),
            priority=org_uavcan_yukon.io.transfer.Priority_1_0(3),
            session=org_uavcan_yukon.io.transfer.Session_0_1(
                subject=org_uavcan_yukon.io.transfer.SubjectSession_0_1(
                    subject_id=uavcan.node.port.SubjectID_1_0(6666), source=[uavcan.node.ID_1_0(1234)]
                )
            ),
            transfer_id=[],
            iface_id=[],
            payload=org_uavcan_yukon.io.transfer.Payload_1_0(b"Hello world!"),
        )
    )

    await asyncio.sleep(0.5)

    # Validate the transfer-ID map.
    assert len(spoofer._transfer_id_map) == 1
    assert list(spoofer._transfer_id_map.keys())[0].source_node_id == 1234
    assert list(spoofer._transfer_id_map.values())[0]._value == 1

    # Configure transports.
    cap_a: typing.List[pyuavcan.transport.Capture] = []
    cap_b: typing.List[pyuavcan.transport.Capture] = []
    target_tr_a = LoopbackTransport(None)
    target_tr_b = LoopbackTransport(None)
    target_tr_a.begin_capture(cap_a.append)
    target_tr_b.begin_capture(cap_b.append)
    spoofer.add_iface(111, target_tr_a)
    spoofer.add_iface(222, target_tr_b)

    # Spoof on both, successfully.
    spoof = Spoof(
        timeout=uavcan.si.unit.duration.Scalar_1_0(1.0),
        priority=org_uavcan_yukon.io.transfer.Priority_1_0(3),
        session=org_uavcan_yukon.io.transfer.Session_0_1(
            subject=org_uavcan_yukon.io.transfer.SubjectSession_0_1(
                subject_id=uavcan.node.port.SubjectID_1_0(6666), source=[uavcan.node.ID_1_0(1234)]
            )
        ),
        transfer_id=[9876543210],  # This transfer will not touch the TID map.
        iface_id=[],  # All ifaces.
        payload=org_uavcan_yukon.io.transfer.Payload_1_0(b"abcd"),
    )
    assert await dcs_pub_spoof.publish(spoof)
    await asyncio.sleep(0.5)

    assert len(cap_a) == len(cap_b)
    (cap,) = cap_a
    cap_a.clear()
    cap_b.clear()
    assert isinstance(cap, LoopbackCapture)
    assert cap.transfer.metadata.transfer_id == 9876543210
    assert len(spoofer._transfer_id_map) == 1  # New entry was not created.
    assert spoofer.status == {
        111: IfaceStatus(num_bytes=4, num_errors=0, num_timeouts=0, num_transfers=1, backlog=0, backlog_peak=0),
        222: IfaceStatus(num_bytes=4, num_errors=0, num_timeouts=0, num_transfers=1, backlog=0, backlog_peak=0),
    }

    # Make one time out, the other raise an error, third one is closed.
    target_tr_a.spoof_result = False
    target_tr_b.spoof_result = RuntimeError("Intended exception")
    target_tr_c = LoopbackTransport(None)
    target_tr_c.close()
    spoofer.add_iface(0, target_tr_c)

    with caplog.at_level(logging.CRITICAL):
        assert await dcs_pub_spoof.publish(spoof)
        await asyncio.sleep(2.0)
    assert not cap_a
    assert not cap_b
    old_status = spoofer.status
    assert old_status == {
        0: IfaceStatus(num_bytes=0, num_errors=1, num_timeouts=0, num_transfers=0, backlog=0, backlog_peak=0),
        111: IfaceStatus(num_bytes=4, num_errors=0, num_timeouts=1, num_transfers=1, backlog=0, backlog_peak=0),
        222: IfaceStatus(num_bytes=4, num_errors=1, num_timeouts=0, num_transfers=1, backlog=0, backlog_peak=0),
    }

    # Force only one iface out of three. Check that the backlog counter goes up.
    spoof.iface_id = [0]
    assert await dcs_pub_spoof.publish(spoof)
    assert await dcs_pub_spoof.publish(spoof)
    assert await dcs_pub_spoof.publish(spoof)
    await asyncio.sleep(2.0)
    assert spoofer.status[0].backlog > 0
    assert spoofer.status[0].backlog_peak > 0
    assert spoofer.status[111] == old_status[111]
    assert spoofer.status[222] == old_status[222]

    # Finalize.
    spoofer.close()
    target_tr_a.close()
    target_tr_b.close()
    target_tr_c.close()
    dcs_pres.close()
    await asyncio.sleep(1.0)
