# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import socket
import numpy
import pyuavcan.transport.udp
import uavcan.metatransport.ethernet
from uavcan.metatransport.ethernet import EtherType_0_1 as EtherType
from . import Transport, Frame, Config


class UDPTransport(Transport):
    NAME = "udp"

    @staticmethod
    def get_capture_payload_size(cap: pyuavcan.transport.Capture) -> int:
        assert isinstance(cap, pyuavcan.transport.udp.UDPCapture)
        return len(cap.link_layer_packet.payload)

    @staticmethod
    def to_dcs_capture(cap: pyuavcan.transport.Capture) -> Frame:
        assert isinstance(cap, pyuavcan.transport.udp.UDPCapture)
        llp = cap.link_layer_packet

        def mk_addr(x: memoryview) -> bytes:
            return x.tobytes().ljust(6, b"\x00")[:6]

        if llp.protocol == socket.AF_INET:
            et = EtherType.IP_V4
        elif llp.protocol == socket.AF_INET6:
            et = EtherType.IP_V6
        else:
            raise ValueError(f"Unsupported protocol: {llp.protocol}")

        return Frame(
            udp=uavcan.metatransport.ethernet.Frame_0_1(
                destination=mk_addr(llp.destination),
                source=mk_addr(llp.source),
                ethertype=et,
                payload=numpy.asarray(llp.payload, dtype=numpy.uint8),
            ),
        )

    @staticmethod
    def from_dcs_capture(ts: pyuavcan.transport.Timestamp, fr: Frame) -> pyuavcan.transport.Capture:
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

    @staticmethod
    def from_dcs_config(cfg: Config) -> pyuavcan.transport.Transport:
        udp_cfg = cfg.udp
        assert udp_cfg
        return pyuavcan.transport.udp.UDPTransport(
            udp_cfg.local_nic_address.value.tobytes().decode(),
            anonymous=True,
            mtu=udp_cfg.mtu,
            service_transfer_multiplier=2 if udp_cfg.duplicate_service_transfers else 1,
        )
