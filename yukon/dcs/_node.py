# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import os
import re
import time
import typing
import logging
import pyuavcan
import pyuavcan.application
from pyuavcan.presentation import Publisher, Subscriber, Client, Server
from uavcan.node import GetInfo_1_0, Heartbeat_1_0, ExecuteCommand_1_1, Version_1_0
from ._logger import setup_log_publisher


UI_NODE_ID = 1
"""
The node-ID of the UI process that coordinates the DCS.
"""

MessageClass = typing.TypeVar("MessageClass", bound=pyuavcan.dsdl.CompositeObject)
ServiceClass = typing.TypeVar("ServiceClass", bound=pyuavcan.dsdl.ServiceObject)

_PORT_NAME_PATTERN = re.compile(r"[a-z][a-z0-9_]*")


_logger = logging.getLogger(__name__)


def _get_parameter(name: str, default: typing.Any = None) -> str:
    full_name = "UAVCAN_" + name.upper().replace(".", "_").replace("-", "_")
    try:
        return os.environ[full_name]
    except LookupError:
        pass
    if default is None:
        raise KeyError(f"Environment variable {full_name!r} is not set and no default value is available") from None
    return str(default)


def _get_port_id(prefix: str, port_name: str, dtype: typing.Type[MessageClass]) -> int:
    if not _PORT_NAME_PATTERN.match(port_name):
        raise ValueError(f"Port name {port_name!r} does not match {_PORT_NAME_PATTERN.pattern!r}")
    return int(_get_parameter(f"{prefix}.{port_name}.id", pyuavcan.dsdl.get_fixed_port_id(dtype)))


class Node(pyuavcan.application.Node):
    def __init__(self, node_name_suffix: str) -> None:
        from yukon import __version_info__

        _logger.debug(
            "Constructing DCS node: name suffix: %r, env vars: %s",
            node_name_suffix,
            list(k for k in os.environ if k.startswith("UAVCAN_")),
        )
        transport = _construct_transport()
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

        setup_log_publisher(self.presentation)
        self.start()

    def make_publisher(self, dtype: typing.Type[MessageClass], port_name: str) -> Publisher[MessageClass]:
        """:raises: :class:`KeyError` if such port is not configured."""
        return self.presentation.make_publisher(dtype, _get_port_id("pub", port_name, dtype))

    def make_subscriber(self, dtype: typing.Type[MessageClass], port_name: str) -> Subscriber[MessageClass]:
        """:raises: :class:`KeyError` if such port is not configured."""
        return self.presentation.make_subscriber(dtype, _get_port_id("sub", port_name, dtype))

    def make_client(
        self, dtype: typing.Type[ServiceClass], port_name: str, server_node_id: int
    ) -> Client[ServiceClass]:
        """:raises: :class:`KeyError` if such port is not configured."""
        return self.presentation.make_client(dtype, _get_port_id("cln", port_name, dtype), server_node_id)

    def get_server(self, dtype: typing.Type[ServiceClass], port_name: str) -> Server[ServiceClass]:
        """:raises: :class:`KeyError` if such port is not configured."""
        return self.presentation.get_server(dtype, _get_port_id("srv", port_name, dtype))

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


def _construct_transport() -> pyuavcan.transport.Transport:
    from ipaddress import ip_address

    try:
        node_id: typing.Optional[int] = int(_get_parameter("node.id.natural16"))
    except LookupError:
        node_id = None

    try:
        udp_addr = ip_address(_get_parameter("udp.ip.string"))
    except LookupError:
        pass
    else:
        from pyuavcan.transport.udp import UDPTransport

        return UDPTransport(udp_addr, local_node_id=node_id)

    try:
        serial_port = _get_parameter("serial.port.string")
    except LookupError:
        pass
    else:
        from pyuavcan.transport.serial import SerialTransport

        return SerialTransport(serial_port, local_node_id=node_id)

    raise ValueError(
        "DCS transport configuration not found in environment variables: "
        + str(list(k for k in os.environ if k.startswith("UAVCAN_")))
    )
