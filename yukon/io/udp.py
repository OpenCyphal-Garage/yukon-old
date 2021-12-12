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
import pyuavcan
from pyuavcan.application.register import Natural8, Natural16
from pyuavcan.transport.udp import UDPTransport
from uavcan.metatransport.ethernet import EtherType_0 as EtherType, Frame_0 as EtherFrame
from org_uavcan_yukon.io.frame import Capture_0 as DSDLCapture, Frame_0 as DSDLFrame
from org_uavcan_yukon.io.iface import OperationalInfo_0 as OperationalInfo
from org_uavcan_yukon.io.transfer import Spoof_0 as DSDLSpoof
import yukon.dcs
from yukon.io import timestamp_to_dsdl, session_from_dsdl


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
                fragmented_payload=[memoryview(msg.payload.payload)],  # type: ignore
            )
            monotonic_deadline = loop.time() + msg.timeout.second
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

    loop = asyncio.get_running_loop()
    sleep_until = loop.time()
    while not local_node.shutdown:
        sleep_until += 1.0
        delay = sleep_until - loop.time()
        if delay > 0:
            await asyncio.sleep(delay)
        await pub_op_info.publish(op_info)
    return 0


def begin_capture(
    op_info: OperationalInfo,
    pub: pyuavcan.presentation.Publisher[DSDLCapture],
    tran: pyuavcan.transport.Transport,
) -> None:
    llp_lookup = {
        socket.AF_INET: EtherType(EtherType.IP_V4),
        socket.AF_INET6: EtherType(EtherType.IP_V6),
    }
    que: asyncio.Queue[pyuavcan.transport.Capture] = asyncio.Queue()

    def mk_adr(x: memoryview) -> bytes:
        return x.tobytes().ljust(6, b"\x00")[:6]

    async def handle_capture(cap: pyuavcan.transport.Capture) -> None:
        assert isinstance(cap, pyuavcan.transport.udp.UDPCapture)
        llp = cap.link_layer_packet
        msg = DSDLCapture(
            timestamp=timestamp_to_dsdl(cap.timestamp),
            sequence_number=op_info.media_frames,
            frame=DSDLFrame(
                udp=EtherFrame(
                    destination=mk_adr(llp.destination),
                    source=mk_adr(llp.source),
                    ethertype=llp_lookup[llp.protocol],
                    payload=numpy.asarray(llp.payload, dtype=numpy.uint8),
                )
            ),
        )
        op_info.media_frames += 1
        op_info.media_bytes += len(cap.link_layer_packet.payload)
        if not await pub.publish(msg):
            op_info.media_capture_failures += 1
            _logger.info("Capture publication timed out: %r", msg)

    async def task() -> None:
        _logger.debug("Capture forwarding task started")
        while True:
            try:
                cap = await que.get()
                await handle_capture(cap)
            except Exception as ex:  # pragma: no cover  pylint: disable=broad-except
                op_info.media_capture_failures += 1
                _logger.exception("Capture handler exception: %s", ex)

    loop = asyncio.get_running_loop()

    def enqueue_threadsafe(cap: pyuavcan.transport.Capture) -> None:  # This is invoked from the worker thread.
        loop.call_soon_threadsafe(que.put_nowait, cap)

    assert 0 == op_info.media_frames
    assert 0 == op_info.media_bytes
    assert 0 == op_info.media_capture_failures
    asyncio.create_task(task(), name="capture_forwarder")
    tran.begin_capture(enqueue_threadsafe)


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
    except Exception as ex:  # pylint: disable=broad-except
        _logger.critical("Process failed: %s", ex, exc_info=True)
        result = 1
    finally:
        node.close()
    _logger.info("Exiting with status %d", result)
    return result


_logger = logging.getLogger(f"yukon.io.{Path(__file__).stem}")


if __name__ == "__main__":
    sys.exit(main())
