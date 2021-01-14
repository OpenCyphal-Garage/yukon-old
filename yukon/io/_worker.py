# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
import asyncio
from pyuavcan.transport import redundant
from pyuavcan.application import Node
from pyuavcan.presentation import Publisher, Subscriber
from org_uavcan_yukon.io.frame import Capture_0_1 as Capture
from org_uavcan_yukon.io.worker import Config_0_1 as Config
from org_uavcan_yukon.io.worker import Feedback_0_1 as Feedback
from org_uavcan_yukon.io.transport import SpoofedTransfer_0_1 as SpoofedTransfer


async def run(
    node: Node,
    pubs_capture: typing.Sequence[Publisher[Capture]],
    pub_feedback: Publisher[Feedback],
    sub_config: Subscriber[Config],
    sub_spoof: Subscriber[SpoofedTransfer],
) -> None:
    try:
        transport = redundant.RedundantTransport()
        transport_init_expr: typing.List[str] = []
    finally:
        node.close()
        await asyncio.wait(asyncio.all_tasks(), timeout=1)
