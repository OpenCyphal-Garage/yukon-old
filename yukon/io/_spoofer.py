# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
import logging
import asyncio
import dataclasses
from collections import defaultdict
import pyuavcan.transport
from pyuavcan.transport import AlienTransfer, AlienTransferMetadata, AlienSessionSpecifier, Priority
from pyuavcan.transport import MessageDataSpecifier, ServiceDataSpecifier, Transport
from pyuavcan.presentation import Subscriber, OutgoingTransferIDCounter
from org_uavcan_yukon.io.transfer import Spoof_0_1 as Spoof


_logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SpoofStatistics:
    num_bytes: int = 0
    num_transfers: int = 0
    num_timeouts: int = 0
    num_errors: int = 0


class Spoofer:
    def __init__(self, dcs_sub_spoof: Subscriber[Spoof]) -> None:
        self._dcs_sub_spoof = dcs_sub_spoof
        self._transfer_id_map: typing.DefaultDict[AlienSessionSpecifier, OutgoingTransferIDCounter] = defaultdict(
            OutgoingTransferIDCounter
        )
        self._inferiors: typing.Dict[int, _Inferior] = {}
        self._task = asyncio.create_task(self._task_fn())

    @property
    def is_alive(self) -> bool:
        return not self._task.done()

    @property
    def statistics(self) -> typing.Dict[int, SpoofStatistics]:
        return {k: e.statistics for k, e in self._inferiors.items()}

    def add_iface(self, iface_id: int, transport: Transport) -> None:
        self._inferiors[iface_id] = _Inferior(SpoofStatistics(), transport)

    def remove_iface(self, iface_id: int) -> None:
        del self._inferiors[iface_id]

    async def _task_fn(self) -> None:
        try:
            async for msg, transfer in self._dcs_sub_spoof:
                _logger.debug("Spoofing %s %s over %d transports", transfer, msg, len(self._inferiors))
                assert isinstance(msg, Spoof)
                await self._spoof(msg)
        except Exception as ex:
            if isinstance(ex, asyncio.CancelledError):
                raise
            if isinstance(ex, pyuavcan.transport.ResourceClosedError):
                return
            _logger.fatal("SPOOFER FAILURE: %s", ex, exc_info=True)

    async def _spoof(self, msg: Spoof) -> None:
        if msg.session.subject:
            try:
                source_node_id = msg.session.subject.source[0].value
            except LookupError:
                source_node_id = None
            ss = AlienSessionSpecifier(
                source_node_id=source_node_id,
                destination_node_id=None,
                data_specifier=MessageDataSpecifier(subject_id=msg.session.subject.subject_id.value),
            )
        elif msg.session.service:
            ss = AlienSessionSpecifier(
                source_node_id=msg.session.service.source.value,
                destination_node_id=msg.session.service.destination.value,
                data_specifier=ServiceDataSpecifier(
                    service_id=msg.session.service.service_id,
                    role=ServiceDataSpecifier.Role.REQUEST
                    if msg.session.service.is_request
                    else ServiceDataSpecifier.Role.RESPONSE,
                ),
            )
        else:
            assert False

        if msg.transfer_id.size:
            transfer_id = int(msg.transfer_id[0])
        else:
            transfer_id = self._transfer_id_map[ss].get_then_increment()

        atr = AlienTransfer(
            metadata=AlienTransferMetadata(
                priority=Priority(msg.priority.value),
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
        await asyncio.gather(*(inf.spoof(atr, monotonic_deadline) for inf in inferiors))


@dataclasses.dataclass
class _Inferior:
    statistics: SpoofStatistics
    transport: Transport

    async def spoof(self, transfer: AlienTransfer, monotonic_deadline: float) -> bool:
        try:
            result = await self.transport.spoof(transfer, monotonic_deadline)
            if result:
                self.statistics.num_bytes += sum(map(len, transfer.fragmented_payload))
                self.statistics.num_transfers += 1
            else:
                self.statistics.num_timeouts += 1
            return result
        except Exception as ex:
            self.statistics.num_errors += 1
            _logger.exception("Spoofing failure %s on transport %s", ex, self.transport)
            return False
