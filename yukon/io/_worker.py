# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
import asyncio
from pyuavcan.transport import redundant
from pyuavcan.application import Node
from pyuavcan.presentation import Publisher, Subscriber
from . import Frame, Configuration, Transfer, Status


async def run(
    node: Node,
    pubs_frame: typing.Sequence[Publisher[Frame]],
    pub_status: Publisher[Status],
    sub_config: Subscriber[Configuration],
    sub_transfer: Subscriber[Transfer],
) -> None:
    try:
        transport = redundant.RedundantTransport()
        transport_init_expr: typing.List[str] = []
    finally:
        node.close()
        await asyncio.wait(asyncio.all_tasks(), timeout=1)
