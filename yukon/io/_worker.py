# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import typing
import logging
import asyncio
import concurrent.futures
from pyuavcan.presentation import Publisher
from org_uavcan_yukon.io import Config_0_1 as IOConfig
from org_uavcan_yukon.io import Status_0_1 as IOStatus
from org_uavcan_yukon.io.iface import Config_0_1 as IOIfaceConfig
import yukon.dcs
from ._spoofer import Spoofer, SpoofStatus, DCSSpoof
from ._captor import DCSCapture, setup_capture_forwarding
from .iface import Iface


MAX_UPDATE_PERIOD = 1.0
"""
An update is always published immediately after each configuration message.
If there are no configuration messages in this amount of time, an update will be published regardless.
"""


class IOWorker:
    def __init__(self) -> None:
        self._node = yukon.dcs.Node("io")
        self._pub_status = self._node.make_publisher(IOStatus, "io_status")
        self._sub_config = self._node.make_subscriber(IOConfig, "io_config")
        self._pub_capture = self._node.make_publisher(DCSCapture, "capture")
        self._spoofer = Spoofer(self._node.make_subscriber(DCSSpoof, "spoof"))
        self._ifaces: typing.Dict[int, typing.Union[Iface, typing.Awaitable[Iface], str]] = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(9999, thread_name_prefix="io_worker_pool")

    async def run(self) -> int:
        while not self._node.shutdown:
            assert set(self._ifaces.keys()) >= set(self._spoofer.status.keys()), "State divergence"
            cfg_transfer = await self._sub_config.receive_for(MAX_UPDATE_PERIOD)
            if cfg_transfer:
                self._reconfigure(cfg_transfer[0])
            await self._update()
        return int(self._node.health)

    def close(self) -> None:
        self._node.close()

    def _reconfigure(self, cfg: IOConfig) -> None:
        _logger.info("Processing %s", cfg)
        to_remove = set(self._ifaces.keys())
        for ifc in cfg.iface_config:
            assert isinstance(ifc, IOIfaceConfig)
            try:
                to_remove.remove(ifc.iface_id)
            except LookupError:
                pass
            if ifc.iface_id in self._ifaces:  # Existing -- nothing to change.
                continue

            _logger.info("Constructing new iface: %s", ifc)
            fut = asyncio.get_event_loop().run_in_executor(self._executor, _initialize_iface, self._pub_capture, ifc)
            assert isinstance(fut, asyncio.Future)
            self._ifaces[ifc.iface_id] = fut

        for iface_id in to_remove:
            item = self._ifaces.pop(iface_id)
            _logger.info("Terminating iface %s: %r", iface_id, item)
            try:
                self._spoofer.remove_iface(iface_id)
            except LookupError:
                pass
            if isinstance(item, Iface):
                asyncio.get_event_loop().run_in_executor(self._executor, item.close)
            elif isinstance(item, asyncio.Future):
                item.cancel()  # Cancel initialization in the worker thread. This may be done after some timeout also.
            elif isinstance(item, str):
                pass  # Already dead, nothing else to do here.
            else:
                assert False

    async def _update(self) -> None:
        from org_uavcan_yukon.io.iface import OperationalInfo_0_1 as OperationalInfo, State_0_1 as IOIfaceState
        from org_uavcan_yukon.io.iface import Status_0_1 as IOIfaceStatus
        from uavcan.primitive import Empty_1_0, String_1_0

        msg = IOStatus()
        spoof_status = self._spoofer.status
        for iface_id, iface in list(self._ifaces.items()):  # Create a copy to allow mutation.
            dcs_iface_state = IOIfaceState()
            if isinstance(iface, asyncio.Future) and iface.done():
                try:
                    iface = iface.result()
                    assert isinstance(iface, Iface)
                    self._spoofer.add_iface(iface_id, iface)
                except Exception as ex:
                    iface = f"Init failed: {type(ex).__name__}: {ex or '<description not available>'}"

            if isinstance(iface, Iface):
                iface_stats = iface.sample_statistics()
                spoof_stats = spoof_status.get(iface_id, SpoofStatus())
                media_utilization_pct = (
                    iface_stats.media_utilization_pct
                    if iface_stats.media_utilization_pct is not None
                    else OperationalInfo.MEDIA_UTILIZATION_PCT_UNKNOWN
                )
                dcs_iface_state.operational = OperationalInfo(
                    media_frames=iface_stats.n_frames,
                    media_bytes=iface_stats.n_media_layer_bytes,
                    media_utilization_pct=media_utilization_pct,
                    errors=iface_stats.n_errors,
                    spoof_bytes=spoof_stats.n_bytes,
                    spoof_transfers=spoof_stats.n_transfers,
                    spoof_timeouts=spoof_stats.n_timeouts,
                    spoof_failures=spoof_stats.n_errors,
                    spoof_backlog_current=spoof_stats.backlog,
                    spoof_backlog_peak=spoof_stats.backlog_peak,
                )
            elif isinstance(iface, str):
                dcs_iface_state.failure = String_1_0(iface)
            elif isinstance(iface, asyncio.Future):
                dcs_iface_state.initialization = Empty_1_0()
            else:
                assert False

            # Concatenation is ugly because we use NumPy arrays.
            msg.iface_status = list(msg.iface_status) + [IOIfaceStatus(iface_id=iface_id, state=dcs_iface_state)]

        if not await self._pub_status.publish(msg):
            _logger.error("IO status publication has timed out")


def _initialize_iface(pub_capture: Publisher[DCSCapture], ifc: IOIfaceConfig) -> Iface:
    iface = Iface.resolve(ifc.config).new(ifc.config)
    setup_capture_forwarding(pub_capture, ifc.iface_id, iface)
    return iface


_logger = logging.getLogger(__name__)
