# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import os
import time
from typing import TypeVar, Type
import asyncio
import logging
import pyuavcan
from pyuavcan.presentation import Publisher, Subscriber, Client, Server
from pyuavcan.application import make_node, register, NodeInfo
from pyuavcan.application.heartbeat_publisher import Heartbeat, Health
from uavcan.node import ExecuteCommand_1_1, Version_1_0

MessageClass = TypeVar("MessageClass", bound=pyuavcan.dsdl.CompositeObject)
ServiceClass = TypeVar("ServiceClass", bound=pyuavcan.dsdl.ServiceObject)


class Node:
    def __init__(self, name_suffix: str) -> None:
        from yukon import __version_info__

        self._shutdown = False
        self._node = pyuavcan.application.make_node(
            NodeInfo(
                software_version=Version_1_0(*__version_info__[:2]),
                name=f"org.uavcan.yukon.{name_suffix}",
            )
        )
        if self._node.id is None:
            raise ValueError("DCS transport configuration error: node cannot be anonymous")

        self._coordinator_node_id = int(
            self._node.registry.setdefault("yukon.dcs.coordinator_node_id", register.Natural16([0xFFFF]))
        )
        self._last_coordinator_heartbeat_at = time.monotonic()

        self._node.heartbeat_publisher.add_pre_heartbeat_handler(self._check_deadman_switch)
        self._node.make_subscriber(Heartbeat).receive_in_background(self._on_heartbeat)
        self._node.get_server(ExecuteCommand_1_1).serve_in_background(self._on_execute_command)
        self._node.start()

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        out = self._node.loop
        assert isinstance(out, asyncio.AbstractEventLoop)
        return out

    @property
    def shutdown(self) -> bool:
        """
        When this value is True, the node MUST be :meth:`close`-d.
        """
        return self._shutdown

    @property
    def health(self) -> Health:
        return self._node.heartbeat_publisher.health

    def make_publisher(self, dtype: Type[MessageClass], port_name: str) -> Publisher[MessageClass]:
        return self._node.make_publisher(dtype, port_name)

    def make_subscriber(self, dtype: Type[MessageClass], port_name: str) -> Subscriber[MessageClass]:
        return self._node.make_subscriber(dtype, port_name)

    def make_client(self, dtype: Type[ServiceClass], server_node_id: int, port_name: str) -> Client[ServiceClass]:
        return self._node.make_client(dtype, server_node_id, port_name)

    def get_server(self, dtype: Type[ServiceClass], port_name: str) -> Server[ServiceClass]:
        return self._node.get_server(dtype, port_name)

    def close(self) -> None:
        self._shutdown = True
        self._node.close()

    def _check_deadman_switch(self) -> None:
        if (time.monotonic() - self._last_coordinator_heartbeat_at) > Heartbeat.OFFLINE_TIMEOUT:
            _logger.error("Coordinator is dead, exiting automatically")
            self._node.heartbeat_publisher.health = Health.ADVISORY
            self._shutdown = True

    async def _on_heartbeat(self, _msg: Heartbeat, meta: pyuavcan.transport.TransferFrom) -> None:
        if meta.source_node_id == self._coordinator_node_id:
            self._last_coordinator_heartbeat_at = time.monotonic()

    async def _on_execute_command(
        self, request: ExecuteCommand_1_1.Request, meta: pyuavcan.presentation.ServiceRequestMetadata
    ) -> ExecuteCommand_1_1.Response:
        _logger.info("Received command %s from %s", request, meta)
        if request.command == ExecuteCommand_1_1.Request.COMMAND_POWER_OFF:
            self._shutdown = True
            return ExecuteCommand_1_1.Response(status=ExecuteCommand_1_1.Response.STATUS_SUCCESS)
        if request.command == ExecuteCommand_1_1.Request.COMMAND_EMERGENCY_STOP:
            os.abort()
        return ExecuteCommand_1_1.Response(status=ExecuteCommand_1_1.Response.STATUS_BAD_COMMAND)


_logger = logging.getLogger(__name__)
