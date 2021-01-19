# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import sys
import typing
import dataclasses
import pyuavcan
from org_uavcan_yukon.io.frame import Frame_0_1 as DCSFrame
from org_uavcan_yukon.io.iface.transport import Config_0_1 as DCSTransportConfig


class Iface:
    TRANSPORT_NAME: str
    """
    Lowercase name of the transport that is also used in DCS unions: "udp", "serial", "can", etc.
    """

    @staticmethod
    def resolve(selector: pyuavcan.dsdl.CompositeObject) -> typing.Type[Iface]:
        for des in _DESCENDANTS:
            if getattr(selector, des.TRANSPORT_NAME, None):
                return des
        raise TypeError(f"No matching transport for {selector}")

    @staticmethod
    def new(cfg: DCSTransportConfig) -> Iface:
        raise NotImplementedError

    @staticmethod
    def convert_capture_from_dcs(ts: pyuavcan.transport.Timestamp, fr: DCSFrame) -> pyuavcan.transport.Capture:
        raise NotImplementedError

    def begin_capture(self, handler: typing.Callable[[IfaceCapture], None]) -> None:
        """
        Wraps :meth:`pyuavcan.transport.Transport.begin_capture`,
        but the callback argument is transformed into :class:`Capture`.
        """
        raise NotImplementedError

    async def spoof(self, transfer: pyuavcan.transport.AlienTransfer, monotonic_deadline: float) -> bool:
        """
        Wraps :meth:`pyuavcan.transport.Transport.spoof`.
        """
        raise NotImplementedError

    def sample_statistics(self) -> IfaceStatistics:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class IfaceCapture:
    timestamp: pyuavcan.transport.Timestamp
    frame: DCSFrame
    # We could also provide the source node-ID for subject sharding purposes (for load balancing),
    # but it would require us to parse and repackage the byte stream for the serial transport
    # because it has no native framing support. May revise this later.


@dataclasses.dataclass
class IfaceStatistics:
    n_frames: int = 0
    n_media_layer_bytes: int = 0
    media_utilization_pct: typing.Optional[int] = None
    n_errors: int = 0


pyuavcan.util.import_submodules(sys.modules[__name__])
_DESCENDANTS = list(pyuavcan.util.iter_descendants(Iface))
