# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import sys
import typing
import logging
from .filesystem import DSDL_NAMESPACES, APP_DIRS

if typing.TYPE_CHECKING:
    import uavcan


_logger = logging.getLogger(__name__)


def ensure_compiled_dsdl() -> None:
    if str(APP_DIRS.compiled_dsdl) not in sys.path:
        sys.path.insert(0, str(APP_DIRS.compiled_dsdl))

    try:
        import uavcan
        import org_uavcan_yukon
    except (ImportError, AttributeError):
        pass
    else:
        return

    import importlib
    from pyuavcan.dsdl import generate_package

    _logger.info("Compiled DSDL packages could not be imported; recompiling...")
    all_ns_dirs = list(DSDL_NAMESPACES.values())
    for ns_dir in all_ns_dirs:
        _logger.debug("Compiling DSDL: %s", ns_dir)
        generate_package(ns_dir, all_ns_dirs, output_directory=APP_DIRS.compiled_dsdl)
    importlib.invalidate_caches()


def make_node_info(name_suffix: str) -> uavcan.node.GetInfo.Response_1_0:
    pass
