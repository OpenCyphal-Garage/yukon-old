#!/usr/bin/env python
# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import sys
import logging
import asyncio
from pathlib import Path
import socket
import numpy
import yukon.dcs
from yukon.io import timestamp_to_dsdl, session_from_dsdl
import pyuavcan
from pyuavcan.application.register import Natural8, Natural16
from pyuavcan.transport.udp import UDPTransport
from uavcan.metatransport.ethernet import EtherType_0_1 as EtherType, Frame_0_1 as EtherFrame
from org_uavcan_yukon.io.frame import Capture_0_1 as DSDLCapture, Frame_0_1 as DSDLFrame
from org_uavcan_yukon.io.iface import OperationalInfo_0_1 as OperationalInfo
from org_uavcan_yukon.io.transfer import Spoof_0_1 as DSDLSpoof


async def run(local_node: yukon.dcs.Node, tran: UDPTransport) -> int:
    op_info = OperationalInfo()

    async def on_spoof(msg: DSDLSpoof, meta: pyuavcan.transport.TransferFrom) -> None:
        try:
            _logger.debug("Spoofing %s / %s", meta, msg)
            atr = pyuavcan.transport.AlienTransfer(
                metadata=pyuavcan.transport.AlienTransferMetadata(
                    priority=pyuavcan.transport.Priority(msg.priority.value),
                    transfer_id=msg.transfer_id,
                    session_specifier=session_from_dsdl(msg.session),
                ),
                fragmented_payload=[memoryview(msg.payload.payload)],
            )
            monotonic_deadline = local_node.loop.time() + msg.timeout.second
            if await tran.spoof(atr, monotonic_deadline):
                op_info.spoof_transfers += 1
                op_info.spoof_bytes += len(msg.payload.payload)
            else:
                op_info.spoof_timeouts += 1
        except Exception:
            op_info.spoof_failures += 1
            raise

    sub_spoof = local_node.make_subscriber(DSDLSpoof, "spoof")
    sub_spoof.receive_in_background(on_spoof)

    begin_capture(
        op_info,
        local_node.make_publisher(DSDLCapture, "capture"),
        tran,
    )

    pub_op_info = local_node.make_publisher(OperationalInfo, "operational_info")

    async def publish_operational_info() -> None:
        op_info.media_utilization_pct = op_info.MEDIA_UTILIZATION_PCT_UNKNOWN
        await pub_op_info.publish(op_info)

    sleep_until = local_node.loop.time()
    while not local_node.shutdown:
        sleep_until += 1.0
        delay = sleep_until - local_node.loop.time()
        if delay > 0:
            await asyncio.sleep(delay)
        await publish_operational_info()
    return 0


def begin_capture(
    op_info: OperationalInfo,
    pub: pyuavcan.presentation.Publisher[DSDLCapture],
    tran: pyuavcan.transport.Transport,
) -> None:
    sequence_number = 0

    def handle_capture(cap: pyuavcan.transport.Capture) -> None:
        nonlocal sequence_number
        assert isinstance(cap, pyuavcan.transport.udp.UDPCapture)

        op_info.media_frames += 1  # Race condition here?
        op_info.media_bytes += len(cap.link_layer_packet.payload)

        llp = cap.link_layer_packet
        if llp.protocol == socket.AF_INET:
            et = EtherType.IP_V4
        elif llp.protocol == socket.AF_INET6:
            et = EtherType.IP_V6
        else:
            _logger.warning("Unsupported transport layer protocol: %r", llp.protocol)
            return

        def mk_adr(x: memoryview) -> bytes:
            return x.tobytes().ljust(6, b"\x00")[:6]

        msg = DSDLCapture(
            timestamp=timestamp_to_dsdl(cap.timestamp),
            sequence_number=sequence_number,
            frame=DSDLFrame(
                udp=EtherFrame(
                    destination=mk_adr(llp.destination),
                    source=mk_adr(llp.source),
                    ethertype=et,
                    payload=numpy.asarray(llp.payload, dtype=numpy.uint8),
                )
            ),
        )
        sequence_number += 1
        asyncio.get_event_loop().call_soon_threadsafe(pub.publish_soon, msg)

    tran.begin_capture(handle_capture)


def main() -> int:
    _logger.info("Starting")
    node = yukon.dcs.Node(f"io.{Path(__file__).stem}")
    try:
        tran = UDPTransport(
            str(node.registry.setdefault("yukon.io.udp.local_ip_address", "")),
            local_node_id=None,  # Always construct anonymous because we use only spoofing for transmission.
            mtu=int(node.registry.setdefault("yukon.io.mtu", Natural16([min(UDPTransport.VALID_MTU_RANGE)]))),
            service_transfer_multiplier=int(
                node.registry.setdefault("yukon.io.service_transfer_multiplier", Natural8([1]))
            ),
        )
        try:
            _logger.info("Constructed transport: %r", tran)
            result = asyncio.get_event_loop_policy().get_event_loop().run_until_complete(run(node, tran))
        finally:
            tran.close()
    except KeyboardInterrupt:
        _logger.info("Interrupted")
        result = 0
    except Exception as ex:
        _logger.critical("Process failed: %s", ex, exc_info=True)
        result = 1
    finally:
        node.close()
    _logger.info("Exiting with status %d", result)
    return result


_logger = logging.getLogger(f"yukon.io.{Path(__file__).stem}")


if __name__ == "__main__":
    sys.exit(main())
