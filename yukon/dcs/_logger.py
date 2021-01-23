# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import sys
from typing import Optional
import logging
import asyncio
import pyuavcan
from uavcan.time import SynchronizedTimestamp_1_0 as SynchronizedTimestamp
from uavcan.diagnostic import Severity_1_0 as Severity, Record_1_1 as Record


def setup_log_publisher(presentation: pyuavcan.presentation.Presentation, logging_level: int = logging.INFO) -> None:
    """
    Setup forwarding of all log messages from :mod:`logging` into the standard fixed subject
    ``uavcan.diagnostic.Record``.
    """
    pub_log = presentation.make_publisher_with_fixed_subject_id(Record)
    pub_log.priority = pyuavcan.transport.Priority.OPTIONAL
    pub_log.send_timeout = 1.0
    logging.root.addHandler(_LogForwarder(logging_level, pub_log))


def log_record_to_dcs(record: logging.LogRecord) -> Record:
    # The magic severity conversion formula is found by a trivial linear regression:
    #   Fit[data, {1, x}, {{0, 0}, {10, 1}, {20, 2}, {30, 4}, {40, 5}, {50, 6}}]
    sev = min(7, round(-0.14285714285714374 + 0.12571428571428572 * record.levelno))
    ts = SynchronizedTimestamp(microsecond=int(record.created * 1e6))
    text = record.getMessage()[:255]  # TODO: this is crude; expose array lengths from DSDL.
    return Record(timestamp=ts, severity=Severity(sev), text=text)


class _LogForwarder(logging.Handler):
    def __init__(self, level: int, publisher: pyuavcan.presentation.Publisher[Record]) -> None:
        super().__init__(level)
        self._pub = publisher
        self._fut: Optional[asyncio.Future[None]] = None

    def emit(self, record: logging.LogRecord) -> None:
        # Drop all low-severity messages from PyUAVCAN to prevent possible positive feedback through the logging system.
        if record.module.startswith(pyuavcan.__name__) and record.levelno < logging.WARNING:
            return

        # Further, unconditionally drop all messages while publishing is in progress for the same reason.
        # This logic may need to be reviewed later.
        if self._fut is not None and self._fut.done():
            self._fut.result()
            self._fut = None

        dcs_rec = log_record_to_dcs(record)
        if self._fut is None:
            self._fut = asyncio.ensure_future(self._publish(dcs_rec))
        else:
            print("LOG FWD DROPPED:", dcs_rec, file=sys.stderr)  # pragma: no cover

    async def _publish(self, record: Record) -> None:
        try:
            if not await self._pub.publish(record):
                print("LOG FWD TIMEOUT:", record, file=sys.stderr)  # pragma: no cover
        except Exception as ex:
            print(f"LOG FWD ERROR: {ex.__class__.__name__}: {ex}", file=sys.stderr)
