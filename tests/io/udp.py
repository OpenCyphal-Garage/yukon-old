# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import sys
import time
from pathlib import Path
import asyncio.subprocess
import contextlib
import pytest
from pyuavcan.transport import (
    OutputSessionSpecifier,
    InputSessionSpecifier,
    MessageDataSpecifier,
    PayloadMetadata,
    Transfer,
    Timestamp,
    Priority,
)
from pyuavcan.application import make_node, make_registry, NodeInfo
from pyuavcan.application.register import ValueProxy, Natural16
from pyuavcan.application.node_tracker import NodeTracker
from pyuavcan.transport.udp import UDPTransport
from uavcan.metatransport.ethernet import EtherType_0 as EtherType
import org_uavcan_yukon
from org_uavcan_yukon.io.frame import Capture_0 as DSDLCapture
from org_uavcan_yukon.io.iface import OperationalInfo_0 as OperationalInfo
from org_uavcan_yukon.io.transfer import Spoof_0 as DSDLSpoof, SubjectSession_0 as DSDLSubjectSession
import uavcan.node
import uavcan.node.port


pytestmark = pytest.mark.asyncio


async def __test_basic() -> None:
    proc = await asyncio.subprocess.create_subprocess_exec(
        sys.executable,
        "-m",
        "yukon.io.udp",
        stdin=asyncio.subprocess.DEVNULL,
        env={
            "UAVCAN__NODE__ID": "2",
            "UAVCAN__UDP__IFACE": "127.42.0.0",
            "UAVCAN__PUB__OPERATIONAL_INFO__ID": "1",
            "UAVCAN__PUB__CAPTURE__ID": "2",
            "UAVCAN__SUB__SPOOF__ID": "3",
            "YUKON__DCS__HEAD_NODE_ID": "0",
            "YUKON__IO__UDP__LOCAL_IP_ADDRESS": "127.66.0.0",
            "YUKON__IO__SERVICE_TRANSFER_MULTIPLIER": "2",
            "PYTHONPATH": str(Path(org_uavcan_yukon.__file__).resolve().parent.parent),
        },
    )
    try:
        reg = make_registry()
        reg.setdefault("uavcan.node.id", ValueProxy(Natural16([0])))
        reg.setdefault("uavcan.udp.iface", "127.42.0.0")
        reg.setdefault("uavcan.sub.operational_info.id", ValueProxy(Natural16([1])))
        reg.setdefault("uavcan.sub.capture.id", ValueProxy(Natural16([2])))
        reg.setdefault("uavcan.pub.spoof.id", ValueProxy(Natural16([3])))
        with make_node(NodeInfo(name="org.uavcan.yukon.test"), reg) as head:
            trk = NodeTracker(head)

            # Ensure the tested process is online and responding.
            await asyncio.sleep(3.0)
            assert len(trk.registry) == 1
            entry = trk.registry[2]
            assert entry.heartbeat.health.value == uavcan.node.Health_1.NOMINAL
            assert entry.info.name.tobytes().decode() == "org.uavcan.yukon.io.udp"

            sub_operational_info = head.make_subscriber(OperationalInfo, "operational_info")
            sub_capture = head.make_subscriber(DSDLCapture, "capture")
            pub_spoof = head.make_publisher(DSDLSpoof, "spoof")

            opi, _ = await sub_operational_info.receive_for(2.0)
            assert isinstance(opi, OperationalInfo)
            assert 0 == opi.media_frames
            assert 0 == opi.media_bytes
            assert 0 == opi.media_capture_failures
            assert 0 == opi.spoof_bytes
            assert 0 == opi.spoof_transfers
            assert 0 == opi.spoof_timeouts
            assert 0 == opi.spoof_failures

            assert not await sub_capture.receive_for(1.0)  # Nothing to capture yet.

            # The network to be sniffed/spoofed on. Note that this is different from the DCS network.
            tr = UDPTransport("127.66.0.88")
            with contextlib.closing(tr):
                pm = PayloadMetadata(100)
                ds = MessageDataSpecifier(7777)

                # The sink session is needed for compatibility with Windows. On Windows, an attempt to transmit to
                # a loopback multicast group for which there are no receivers may fail with the following errors:
                #   OSError: [WinError 10051]   A socket operation was attempted to an unreachable network
                #   OSError: [WinError 1231]    The network location cannot be reached. For information about network
                #                               troubleshooting, see Windows Help
                si = tr.get_input_session(InputSessionSpecifier(ds, None), pm)
                assert si  # We don't really need to use it.

                so = tr.get_output_session(OutputSessionSpecifier(ds, None), pm)
                assert await so.send(
                    Transfer(
                        Timestamp.now(),
                        Priority.LOW,
                        transfer_id=9876543210,
                        fragmented_payload=[memoryview(b"qwerty")],
                    ),
                    monotonic_deadline=asyncio.get_running_loop().time() + 1.0,
                )

                # The worker should catch the frame we just sent.
                cap, _ = await sub_capture.receive_for(1.0)
                assert isinstance(cap, DSDLCapture)
                print(cap)
                assert abs(cap.timestamp.microsecond * 1e-6 - time.time()) < 1.0
                assert 0 == cap.sequence_number
                assert cap.frame.udp.ethertype.value == EtherType.IP_V4
                assert b"qwerty" in cap.frame.udp.payload.tobytes()
                assert 9876543210 .to_bytes(7, "little") in cap.frame.udp.payload.tobytes()

                # Ensure the stats are updated.
                while await sub_operational_info.receive_for(0.1):  # Fetch the latest ignore the rest.
                    pass
                opi, _ = await sub_operational_info.receive_for(2.0)
                assert isinstance(opi, OperationalInfo)
                assert 1 == opi.media_frames
                assert len(cap.frame.udp.payload) == opi.media_bytes
                assert 0 == opi.media_capture_failures
                assert 0 == opi.spoof_bytes
                assert 0 == opi.spoof_transfers
                assert 0 == opi.spoof_timeouts
                assert 0 == opi.spoof_failures

                # Send a different frame.
                assert await so.send(
                    Transfer(
                        Timestamp.now(),
                        Priority.LOW,
                        transfer_id=1234567890,
                        fragmented_payload=[memoryview(b"asdf0123456789")],
                    ),
                    monotonic_deadline=asyncio.get_running_loop().time() + 1.0,
                )

                # The worker should catch the frame we just sent.
                cap, _ = await sub_capture.receive_for(1.0)
                assert isinstance(cap, DSDLCapture)
                print(cap)
                assert abs(cap.timestamp.microsecond * 1e-6 - time.time()) < 1.0
                assert 1 == cap.sequence_number
                assert cap.frame.udp.ethertype.value == EtherType.IP_V4
                assert b"asdf0123456789" in cap.frame.udp.payload.tobytes()
                assert 1234567890 .to_bytes(7, "little") in cap.frame.udp.payload.tobytes()

                # Ensure the stats are updated.
                old_media_bytes = opi.media_bytes
                while await sub_operational_info.receive_for(0.1):  # Fetch the latest ignore the rest.
                    pass
                opi, _ = await sub_operational_info.receive_for(2.0)
                assert isinstance(opi, OperationalInfo)
                assert 2 == opi.media_frames
                assert len(cap.frame.udp.payload) + old_media_bytes == opi.media_bytes
                assert 0 == opi.media_capture_failures
                assert 0 == opi.spoof_bytes
                assert 0 == opi.spoof_transfers
                assert 0 == opi.spoof_timeouts
                assert 0 == opi.spoof_failures

                # Nothing more to capture.
                assert not await sub_capture.receive_for(1.0)

                # Spoof one frame. It should be captured, too.
                spoof = DSDLSpoof()
                spoof.timeout.second = 1.0
                spoof.transfer_id = 1234567890
                spoof.priority.value = spoof.priority.FAST
                spoof.payload.payload = "payload"
                spoof.session.subject = DSDLSubjectSession(
                    subject_id=uavcan.node.port.SubjectID_1(7777),
                    source=[uavcan.node.ID_1(3210)],
                )
                assert await pub_spoof.publish(spoof)

                # TODO: the rest cannot be tested because spoofing is not yet implemented for the UDP transport.
    finally:
        with contextlib.suppress(Exception):
            proc.kill()
        await asyncio.sleep(1.0)  # Wait for the pending tasks to terminate.
