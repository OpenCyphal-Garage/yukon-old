# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import copy
import typing
import socket
import logging
import numpy
import pyuavcan.transport.udp
import uavcan.metatransport.ethernet
from uavcan.metatransport.ethernet import EtherType_0_1 as EtherType
from . import Iface, DCSFrame, DCSTransportConfig, IfaceCapture, IfaceStatistics


_logger = logging.getLogger(__name__)


class UDPIface(Iface):
    TRANSPORT_NAME = "udp"

    def __init__(self, transport: pyuavcan.transport.Transport) -> None:
        self._transport = transport
        self._capture_handlers: typing.List[typing.Callable[[IfaceCapture], None]] = []
        self._stats = IfaceStatistics()

    @staticmethod
    def new(cfg: DCSTransportConfig) -> UDPIface:
        udp_cfg = cfg.udp
        assert udp_cfg
        tr = pyuavcan.transport.udp.UDPTransport(
            udp_cfg.local_nic_address.value.tobytes().decode(),
            local_node_id=None,
            mtu=udp_cfg.mtu,
            service_transfer_multiplier=2 if udp_cfg.duplicate_service_transfers else 1,
        )
        return UDPIface(tr)

    @staticmethod
    def capture_from_dcs(ts: pyuavcan.transport.Timestamp, fr: DCSFrame) -> pyuavcan.transport.Capture:
        udp_frame = fr.udp
        assert udp_frame

        if udp_frame.ethertype.value == EtherType.IP_V4:
            proto = socket.AF_INET
        elif udp_frame.ethertype.value == EtherType.IP_V6:
            proto = socket.AF_INET6
        else:
            raise ValueError(f"Unsupported ethertype: 0x{udp_frame.ethertype.value:04x}")

        return pyuavcan.transport.udp.UDPCapture(
            timestamp=ts,
            link_layer_packet=pyuavcan.transport.udp.LinkLayerPacket(
                protocol=proto,
                source=udp_frame.source.data,
                destination=udp_frame.destination.data,
                payload=udp_frame.payload.data,
            ),
        )

    def begin_capture(self, handler: typing.Callable[[IfaceCapture], None]) -> None:
        if not self._capture_handlers:
            self._transport.begin_capture(self._process_capture)
        self._capture_handlers.append(handler)

    async def spoof(self, transfer: pyuavcan.transport.AlienTransfer, monotonic_deadline: float) -> bool:
        return await self._transport.spoof(transfer, monotonic_deadline)

    def sample_statistics(self) -> IfaceStatistics:
        return copy.copy(self._stats)

    def close(self) -> None:
        self._transport.close()

    def _process_capture(self, cap: pyuavcan.transport.Capture) -> None:
        assert isinstance(cap, pyuavcan.transport.udp.UDPCapture)

        def mk_addr(x: memoryview) -> bytes:
            return x.tobytes().ljust(6, b"\x00")[:6]

        llp = cap.link_layer_packet
        if llp.protocol == socket.AF_INET:
            et = EtherType.IP_V4
        elif llp.protocol == socket.AF_INET6:
            et = EtherType.IP_V6
        else:
            _logger.warning("%s: Unsupported transport layer protocol: %r", self, llp.protocol)
            return

        dcs = DCSFrame(
            udp=uavcan.metatransport.ethernet.Frame_0_1(
                destination=mk_addr(llp.destination),
                source=mk_addr(llp.source),
                ethertype=et,
                payload=numpy.asarray(llp.payload, dtype=numpy.uint8),
            ),
        )

        self._stats.n_frames += 1
        self._stats.n_media_layer_bytes += len(llp.payload)
        # TODO: populate the media utilization estimate (requires querying the OS network iface speed).
        # Error counts are not provided because UDPTransport does not provide the required stats. May change this later.

        iface_cap = IfaceCapture(timestamp=cap.timestamp, frame=dcs)
        _logger.debug("%s: Captured %r", self, iface_cap)
        pyuavcan.util.broadcast(self._capture_handlers)(iface_cap)

    def __repr__(self) -> str:
        return pyuavcan.util.repr_attributes(self, self._transport)
