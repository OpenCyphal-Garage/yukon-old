# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
import logging
import pyuavcan
from pyuavcan.transport import Timestamp
from org_uavcan_yukon.io.frame import Frame_0_1 as Frame


_logger = logging.getLogger(__name__)


def make_pyuavcan_capture(ts: Timestamp, fr: Frame, own_spoof: bool) -> pyuavcan.transport.Capture:
    pass


def parse_pyuavcan_capture(cap: pyuavcan.transport.Capture) -> typing.Tuple[Frame, bool]:
    pass
