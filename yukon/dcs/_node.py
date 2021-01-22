# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import os
import time
import typing
import logging
import pyuavcan
import pyuavcan.application
from pyuavcan.presentation import Publisher, Subscriber, Client, Server
from uavcan.node import GetInfo_1_0, Heartbeat_1_0, ExecuteCommand_1_1, Version_1_0
import uavcan.register
import uavcan.time
from ._logger import setup_log_publisher
from . import register


UI_NODE_ID = 1
"""
The node-ID of the UI process that coordinates the DCS.
"""

MessageClass = typing.TypeVar("MessageClass", bound=pyuavcan.dsdl.CompositeObject)
ServiceClass = typing.TypeVar("ServiceClass", bound=pyuavcan.dsdl.ServiceObject)


_logger = logging.getLogger(__name__)


class Node(pyuavcan.application.Node):
    def __init__(self, node_name_suffix: str) -> None:
        from yukon import __version_info__

        _logger.debug(
            "Constructing DCS node: name suffix: %r, env vars: %s",
            node_name_suffix,
            list(k for k in os.environ if k.startswith("UAVCAN_")),
        )
        transport = self._construct_transport()
        if transport.local_node_id is None:
            raise ValueError("DCS transport configuration error: node cannot be anonymous")

        presentation = pyuavcan.presentation.Presentation(transport)

        node_info = GetInfo_1_0.Response(
            protocol_version=Version_1_0(*pyuavcan.UAVCAN_SPECIFICATION_VERSION),
            software_version=Version_1_0(*__version_info__[:2]),
            name=f"org.uavcan.yukon.{node_name_suffix}",
        )
        super().__init__(presentation, info=node_info, with_diagnostic_subscriber=False)

        self.heartbeat_publisher.add_pre_heartbeat_handler(self._check_deadman_switch)

        self._sub_heartbeat = presentation.make_subscriber_with_fixed_subject_id(Heartbeat_1_0)
        self._sub_heartbeat.receive_in_background(self._on_heartbeat)
        self._last_ui_heartbeat_at = time.monotonic()

        self._registry = register.Registry()
        for n, v in register.parse_environment_variables():
            self._registry.create(n, v)
        self._srv_register_access = self.presentation.get_server_with_fixed_service_id(uavcan.register.Access_1_0)
        self._srv_register_list = self.presentation.get_server_with_fixed_service_id(uavcan.register.List_1_0)

        setup_log_publisher(self.presentation)
        self.start()

    def start(self) -> None:
        super().start()
        self._srv_register_access.serve_in_background(self._on_register_access)
        self._srv_register_list.serve_in_background(self._on_register_list)

    def close(self) -> None:
        super().close()  # There is no need to close each port separately, it's automated.
        self._registry.close()

    def make_publisher(self, dtype: typing.Type[MessageClass], port_name: str) -> Publisher[MessageClass]:
        """:raises: :class:`KeyError` if such port is not configured."""
        return self.presentation.make_publisher(dtype, self._get_port_id("pub", port_name, dtype))

    def make_subscriber(self, dtype: typing.Type[MessageClass], port_name: str) -> Subscriber[MessageClass]:
        """:raises: :class:`KeyError` if such port is not configured."""
        return self.presentation.make_subscriber(dtype, self._get_port_id("sub", port_name, dtype))

    def make_client(
        self, dtype: typing.Type[ServiceClass], port_name: str, server_node_id: int
    ) -> Client[ServiceClass]:
        """:raises: :class:`KeyError` if such port is not configured."""
        return self.presentation.make_client(dtype, self._get_port_id("cln", port_name, dtype), server_node_id)

    def get_server(self, dtype: typing.Type[ServiceClass], port_name: str) -> Server[ServiceClass]:
        """:raises: :class:`KeyError` if such port is not configured."""
        return self.presentation.get_server(dtype, self._get_port_id("srv", port_name, dtype))

    def _on_heartbeat(self, _msg: Heartbeat_1_0, transfer: pyuavcan.transport.TransferFrom) -> None:
        if transfer.source_node_id == UI_NODE_ID:
            self._last_ui_heartbeat_at = time.monotonic()

    def _on_execute_command(
        self, request: ExecuteCommand_1_1.Request, meta: pyuavcan.presentation.ServiceRequestMetadata
    ) -> ExecuteCommand_1_1.Response:
        _logger.info("Received command %s from %s", request, meta)
        if request.command == ExecuteCommand_1_1.Request.COMMAND_POWER_OFF:
            self.presentation.transport.loop.call_later(0.5, self.close)
            return ExecuteCommand_1_1.Response(status=ExecuteCommand_1_1.Response.STATUS_SUCCESS)

        if request.command == ExecuteCommand_1_1.Request.COMMAND_EMERGENCY_STOP:
            os.abort()

        return ExecuteCommand_1_1.Response(status=ExecuteCommand_1_1.Response.STATUS_BAD_COMMAND)

    def _check_deadman_switch(self) -> None:
        if (time.monotonic() - self._last_ui_heartbeat_at) > Heartbeat_1_0.OFFLINE_TIMEOUT:
            _logger.error("UI node is dead, exiting automatically")
            self.presentation.transport.loop.call_soon(self.close)

    async def _on_register_access(
        self, request: uavcan.register.Access_1_0.Request, meta: pyuavcan.presentation.ServiceRequestMetadata
    ) -> uavcan.register.Access_1_0.Response:
        _logger.debug("Register access %r %r", request, meta)
        entry = self._registry.access(request.name.name.tobytes().decode(), request.value)
        response = uavcan.register.Access_1_0.Response(
            timestamp=uavcan.time.SynchronizedTimestamp_1_0(microsecond=int(time.time() * 1e6)),
            mutable=entry.mutable,
            persistent=self._registry.persistent,
            value=entry.value,
        )
        return response

    async def _on_register_list(
        self, request: uavcan.register.List_1_0.Request, meta: pyuavcan.presentation.ServiceRequestMetadata
    ) -> uavcan.register.List_1_0.Response:
        _logger.debug("Register list %r %r", request, meta)
        response = uavcan.register.List_1_0.Response()
        name = self._registry.get_name_at_index(request.index)
        if name is not None:
            response.name.name = name
        return response

    def _get_port_id(self, kind: str, port_name: str, dtype: typing.Type[MessageClass]) -> int:
        name = f"uavcan.{kind}.{port_name}.id"
        reg = self._registry.get_concrete(name, register.Natural16)
        if reg is not None:
            return int(reg.value[0])
        fixed = pyuavcan.dsdl.get_fixed_port_id(dtype)
        if fixed is not None:
            return fixed
        raise register.MissingRegisterError(f"Register {name} is invalid and {dtype} does not define a fixed port-ID")

    def _construct_transport(self) -> pyuavcan.transport.Transport:
        u16 = self._registry.get_concrete("uavcan.node.id", register.Natural16)
        node_id = None if u16 is None else int(u16.value[0])

        s = self._registry.get_concrete("uavcan.udp.ip", register.String)
        if s:
            from pyuavcan.transport.udp import UDPTransport
            from ipaddress import ip_address

            udp_addr = ip_address(s.value.tobytes().decode())
            return UDPTransport(udp_addr, local_node_id=node_id)

        s = self._registry.get_concrete("uavcan.serial.port", register.String)
        if s:
            from pyuavcan.transport.serial import SerialTransport

            return SerialTransport(s.value.tobytes().decode(), local_node_id=node_id)

        raise ValueError(
            "DCS transport configuration not found in environment variables: "
            + str(list(k for k in os.environ if k.startswith("UAVCAN_")))
        )
