# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import logging
import pyuavcan
from uavcan.time import SynchronizedTimestamp_1_0 as SynchronizedTimestamp
from uavcan.diagnostic import Severity_1_0 as Severity, Record_1_1 as Record


def setup_log_publisher(presentation: pyuavcan.presentation.Presentation) -> None:
    """
    Setup forwarding of all log messages from :mod:`logging` into the standard fixed subject
    ``uavcan.diagnostic.Record``.

    The default severity is :data:`logging.INFO` (log records at lower severity will be ignored).
    Logging at lower severity levels is difficult because that may lead to infinite recursion.
    """
    pub_log = presentation.make_publisher_with_fixed_subject_id(Record)

    class LogForwarder(logging.Handler):
        def __init__(self) -> None:
            self._recursion = False
            super().__init__(logging.INFO)

        def emit(self, record: logging.LogRecord) -> None:
            if self._recursion:  # Prevent recursive calls from the publisher we are invoking.
                return
            try:
                self._recursion = True
                pub_log.publish_soon(log_record_to_dcs(record))
            finally:
                self._recursion = False

    logging.root.addHandler(LogForwarder())


def log_record_to_dcs(record: logging.LogRecord) -> Record:
    # The magic severity conversion formula is found by a trivial linear regression:
    #   Fit[data, {1, x}, {{0, 0}, {10, 1}, {20, 2}, {30, 4}, {40, 5}, {50, 6}}]
    sev = min(7, round(-0.14285714285714374 + 0.12571428571428572 * record.levelno))
    ts = SynchronizedTimestamp(microsecond=int(record.created * 1e6))
    text = record.getMessage()[:255]  # TODO: this is crude; expose array lengths from DSDL.
    return Record(timestamp=ts, severity=Severity(sev), text=text)
