# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
import logging
import asyncio
import dataclasses
from collections import defaultdict
import pyuavcan
from pyuavcan.transport import AlienTransfer, AlienTransferMetadata, AlienSessionSpecifier, ResourceClosedError
from pyuavcan.presentation import Subscriber, OutgoingTransferIDCounter
from org_uavcan_yukon.io.transfer import Spoof_0_1 as DCSSpoof
from . import session_from_dcs
from .iface import Iface


_logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SpoofStatus:
    n_bytes: int = 0
    n_transfers: int = 0
    n_timeouts: int = 0
    n_errors: int = 0
    backlog: int = 0
    backlog_peak: int = 0


class Spoofer:
    def __init__(self, dcs_sub_spoof: Subscriber[DCSSpoof]) -> None:
        self._transfer_id_map: typing.DefaultDict[AlienSessionSpecifier, OutgoingTransferIDCounter] = defaultdict(
            OutgoingTransferIDCounter
        )
        self._inferiors: typing.Dict[int, _Inferior] = {}
        dcs_sub_spoof.receive_in_background(self._on_spoof_message)

    @property
    def status(self) -> typing.Dict[int, SpoofStatus]:
        return {k: e.status for k, e in self._inferiors.items()}

    def add_iface(self, iface_id: int, iface: Iface) -> None:
        self._inferiors[iface_id] = _Inferior(iface)

    def remove_iface(self, iface_id: int) -> None:
        self._inferiors.pop(iface_id).close()

    def close(self) -> None:
        for k in list(self._inferiors):
            self.remove_iface(k)

    async def _on_spoof_message(self, msg: DCSSpoof, transfer: pyuavcan.transport.TransferFrom) -> None:
        _logger.debug("Spoofing %s %s over %d ifaces", transfer, msg, len(self._inferiors))
        ss = session_from_dcs(msg.session)

        if msg.transfer_id.size:
            transfer_id = int(msg.transfer_id[0])
        else:
            transfer_id = self._transfer_id_map[ss].get_then_increment()

        # noinspection PyArgumentList
        atr = AlienTransfer(
            metadata=AlienTransferMetadata(
                priority=pyuavcan.transport.Priority(msg.priority.value),
                transfer_id=transfer_id,
                session_specifier=ss,
            ),
            fragmented_payload=[memoryview(msg.payload.payload)],
        )

        inferiors: typing.Iterable[_Inferior]
        if msg.iface_id.size:
            try:
                inferiors = (self._inferiors[int(msg.iface_id[0])],)
            except LookupError:
                inferiors = []  # No such interface -- do nothing.
        else:
            inferiors = self._inferiors.values()
        monotonic_deadline = asyncio.get_event_loop().time() + msg.timeout.second
        for inf in inferiors:
            inf.push(atr, monotonic_deadline)


class _Inferior:
    def __init__(self, iface: Iface) -> None:
        self._status = SpoofStatus()
        self._iface = iface
        self._queue: asyncio.Queue[typing.Tuple[AlienTransfer, float]] = asyncio.Queue()
        self._task = asyncio.create_task(self._task_fn())

    @property
    def status(self) -> SpoofStatus:
        from copy import copy

        return copy(self._status)

    def push(self, transfer: AlienTransfer, monotonic_deadline: float) -> None:
        self._update_status()
        self._queue.put_nowait((transfer, monotonic_deadline))

    def close(self) -> None:
        self._task.cancel()

    def _update_status(self) -> None:
        self._status.backlog = self._queue.qsize()
        self._status.backlog_peak = max(self._status.backlog_peak, self._status.backlog)

    async def _task_fn(self) -> None:
        try:
            while True:
                self._update_status()
                transfer, monotonic_deadline = await self._queue.get()
                await self._do_spoof(transfer, monotonic_deadline)
        except asyncio.CancelledError:
            pass
        except ResourceClosedError:
            _logger.warning("Spoofer worker for %s is stopping because the iface is closed", self._iface)
        except Exception as ex:
            _logger.fatal("Spoofer worker for %s has failed: %s", self._iface, ex, exc_info=True)

    async def _do_spoof(self, transfer: AlienTransfer, monotonic_deadline: float) -> None:
        try:
            result = await self._iface.spoof(transfer, monotonic_deadline)
            if result:
                self._status.n_bytes += sum(map(len, transfer.fragmented_payload))
                self._status.n_transfers += 1
            else:
                self._status.n_timeouts += 1
        except Exception as ex:
            self._status.n_errors += 1
            if isinstance(ex, (asyncio.CancelledError, ResourceClosedError)):
                raise
            _logger.exception("Could not spoof on %s because: %s", self._iface, ex)
