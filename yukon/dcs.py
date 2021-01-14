# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import logging
import pyuavcan
import uavcan.node


_logger = logging.getLogger(__name__)


def make_node_info(name_suffix: str) -> uavcan.node.GetInfo_1_0.Response:
    from yukon import __version_info__

    return uavcan.node.GetInfo_1_0.Response(
        protocol_version=uavcan.node.Version_1_0(*pyuavcan.UAVCAN_SPECIFICATION_VERSION),
        software_version=uavcan.node.Version_1_0(*__version_info__[:2]),
        name=f"org.uavcan.yukon.{name_suffix}",
    )
