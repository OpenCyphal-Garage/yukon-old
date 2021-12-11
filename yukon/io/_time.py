# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import time
import pyuavcan
import uavcan.time


def timestamp_to_dsdl(ts: pyuavcan.transport.Timestamp) -> uavcan.time.SynchronizedTimestamp_1:
    """
    System (wall) timestamp is repackaged into the DSDL object.
    Monotonic timestamp is discarded because it is only valid in the local machine (and possibly only this process).
    """
    return uavcan.time.SynchronizedTimestamp_1(microsecond=ts.system_ns // 1000)


def timestamp_from_dsdl(ts: uavcan.time.SynchronizedTimestamp_1) -> pyuavcan.transport.Timestamp:
    """
    System (wall) timestamp is fetched from the supplied DSDL object.
    Monotonic timestamp is sampled from :func:`time.monotonic_ns`.
    Monotonic timestamps cannot be transferred over the network because monotonic clocks are never synchronized.
    """
    return pyuavcan.transport.Timestamp(system_ns=ts.microsecond * 1000, monotonic_ns=time.monotonic_ns())
