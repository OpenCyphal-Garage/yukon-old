# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
import logging
import asyncio
import pyuavcan.transport
from pyuavcan.application import Node
from pyuavcan.presentation import Publisher, Subscriber
from org_uavcan_yukon.io.frame import Capture_0_1 as Capture
from org_uavcan_yukon.io import Config_0_1 as Config
from org_uavcan_yukon.io import Status_0_1 as Status
from org_uavcan_yukon.io.transfer import Spoof_0_1 as Spoof
from ._spoofer import Spoofer


_logger = logging.getLogger(__name__)


class IOWorker:
    def __init__(
        self,
        node: Node,
        pubs_capture: typing.Sequence[Publisher[Capture]],
        pub_status: Publisher[Status],
        sub_config: Subscriber[Config],
        sub_spoof: Subscriber[Spoof],
    ) -> None:
        self._node = node
        self._dcs_pub_status = pub_status
        self._dsc_sub_config = sub_config
        self._spoofer = Spoofer(sub_spoof)

    async def run(self) -> None:
        try:
            pass
        except (pyuavcan.transport.ResourceClosedError, asyncio.CancelledError):
            pass
        except Exception as ex:
            _logger.fatal("IO worker failed: %s", ex)
        finally:
            self._node.close()
            await asyncio.wait(asyncio.all_tasks(), timeout=1)
