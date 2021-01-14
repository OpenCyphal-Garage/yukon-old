# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import logging
import pyuavcan
import pyuavcan.application
import uavcan.node
import yukon.transport


_logger = logging.getLogger(__name__)


def construct_node(
    dcs_transport_expr: str,
    node_name_suffix: str,
    allow_anonymity: bool = False,
) -> pyuavcan.application.Node:
    from yukon import __version_info__

    _logger.debug(
        "Constructing DCS node: DCS transport %r, name suffix %r, allow anonymity: %r",
        dcs_transport_expr,
        node_name_suffix,
        allow_anonymity,
    )

    transport = yukon.transport.construct(dcs_transport_expr)
    if transport.local_node_id is None and not allow_anonymity:
        raise ValueError("DCS transport configuration error: this node cannot be anonymous")

    presentation = pyuavcan.presentation.Presentation(transport)

    node_info = uavcan.node.GetInfo_1_0.Response(
        protocol_version=uavcan.node.Version_1_0(*pyuavcan.UAVCAN_SPECIFICATION_VERSION),
        software_version=uavcan.node.Version_1_0(*__version_info__[:2]),
        name=f"org.uavcan.yukon.{node_name_suffix}",
    )

    node = pyuavcan.application.Node(presentation, info=node_info, with_diagnostic_subscriber=False)

    # TODO: configure a logging publisher to sink log records from "logging" into the DCS network.

    _logger.debug("Constructed DCS node: %s", node)
    return node
