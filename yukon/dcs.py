# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import os
import time
import typing
import inspect
import logging
import pyuavcan
import pyuavcan.application
from uavcan.node import GetInfo_1_0, Heartbeat_1_0, ExecuteCommand_1_1, Version_1_0


UI_NODE_ID = 1
"""
The node-ID of the UI process that coordinates the DCS.
"""


_logger = logging.getLogger(__name__)


class Node(pyuavcan.application.Node):
    def __init__(self, dcs_transport_expr: str, node_name_suffix: str) -> None:
        from yukon import __version_info__

        _logger.debug("Constructing DCS node: DCS transport %r, name suffix %r", dcs_transport_expr, node_name_suffix)

        transport = _construct_transport(dcs_transport_expr)
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

        # TODO: configure a logging publisher to sink log records from "logging" into the DCS network.

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


def _construct_transport(expression: str) -> pyuavcan.transport.Transport:
    context = _make_transport_evaluation_context()
    out = eval(expression, context)
    _logger.debug("Expression %r yields %r", expression, out)
    if not isinstance(out, pyuavcan.transport.Transport):
        raise ValueError(
            f"The expression {expression!r} yields an instance of {type(out).__name__}. "
            f"Expected an instance of pyuavcan.transport.Transport."
        )
    return out


def _make_transport_evaluation_context() -> typing.Dict[str, typing.Any]:
    def handle_import_error(parent_module_name: str, ex: ImportError) -> None:
        try:
            tr = parent_module_name.split(".")[2]
        except LookupError:
            tr = parent_module_name
        _logger.info("Transport %r is not available due to the missing dependency %r", tr, ex.name)

    # noinspection PyTypeChecker
    pyuavcan.util.import_submodules(pyuavcan.transport, error_handler=handle_import_error)

    context: typing.Dict[str, typing.Any] = {
        "pyuavcan": pyuavcan,
    }

    # Expose pre-imported transport modules for convenience.
    for name, module in inspect.getmembers(pyuavcan.transport, inspect.ismodule):
        if not name.startswith("_"):
            context[name] = module

    # Pre-import transport classes for convenience.
    transport_base = pyuavcan.transport.Transport
    # Suppressing MyPy false positive: https://github.com/python/mypy/issues/5374
    for cls in pyuavcan.util.iter_descendants(transport_base):  # type: ignore
        if not cls.__name__.startswith("_") and cls is not transport_base:
            name = cls.__name__.rpartition(transport_base.__name__)[0]
            assert name
            context[name] = cls

    _logger.debug("Transport expression evaluation context (on the next line):\n%r", context)
    return context
