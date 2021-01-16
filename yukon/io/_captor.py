# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
import asyncio
import dataclasses
import pyuavcan
from org_uavcan_yukon.io.frame import Capture_0_1 as Capture
from org_uavcan_yukon.io.frame import Frame_0_1 as Frame
from . import to_dcs_timestamp


@dataclasses.dataclass
class CaptureStatistics:
    num_frames: int = 0
    num_bytes: int = 0


class Captor:
    def __init__(
        self,
        dcs_pub_capture: pyuavcan.presentation.Publisher[Capture],
        capture_converter: typing.Callable[[pyuavcan.transport.Capture], typing.Tuple[Frame, int]],
        iface_id: int,
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        self._pub = dcs_pub_capture
        self._conv = capture_converter
        self._iface_id = int(iface_id)
        self._stats = CaptureStatistics()
        self._loop = loop

    def dispatch_capture(self, cap: pyuavcan.transport.Capture) -> None:
        frame, payload_size = self._conv(cap)
        msg = Capture(
            timestamp=to_dcs_timestamp(cap.timestamp),
            iface_id=self._iface_id,
            sequence_number=self._stats.num_frames,
            frame=frame,
        )
        self._stats.num_frames += 1
        self._stats.num_bytes += payload_size
        self._loop.call_soon_threadsafe(self._pub.publish_soon, msg)
