# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import asyncio
import logging
from pyuavcan.presentation import Publisher
from org_uavcan_yukon.io.frame import Capture_0_1 as DCSCapture
from . import to_dcs_timestamp
from .iface import IfaceCapture, Iface


_logger = logging.getLogger(__name__)


def setup_capture_forwarding(dcs_pub_capture: Publisher[DCSCapture], iface_id: int, iface: Iface) -> None:
    sequence_number = 0

    def handle_capture(cap: IfaceCapture) -> None:
        nonlocal sequence_number
        msg = DCSCapture(
            timestamp=to_dcs_timestamp(cap.timestamp),
            iface_id=iface_id,
            sequence_number=sequence_number,
            frame=cap.frame,
        )
        sequence_number += 1
        asyncio.get_event_loop().call_soon_threadsafe(dcs_pub_capture.publish_soon, msg)

    iface.begin_capture(handle_capture)
    _logger.info("Set up capture on iface_id=%r: %r", iface_id, iface)
