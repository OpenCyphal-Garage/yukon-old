# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>
# pylint: disable=wrong-import-position

import os
import sys
from pathlib import Path
from importlib.resources import read_text as _read_text
import coloredlogs


if sys.version_info < (3, 10):
    raise RuntimeError("A newer version of Python is required")


__version__ = _read_text(__name__, "VERSION", encoding="utf8").strip()
__version_info__ = tuple(map(int, __version__.split(".")[:3]))
__author__ = "UAVCAN Consortium"
__email__ = "consortium@uavcan.org"
__copyright__ = f"Copyright (c) 2021 {__author__} <{__email__}>"
__license__ = "MIT"


coloredlogs.install(level=os.getenv("YUKON_LOGLEVEL", "INFO"))


PACKAGE_ROOT_DIR = Path(__file__).resolve().parent
COMPILED_DSDL_DIR = PACKAGE_ROOT_DIR / "_compiled"

sys.path.insert(0, str(COMPILED_DSDL_DIR))

import uavcan
import org_uavcan_yukon

sys.path.remove(str(COMPILED_DSDL_DIR))

from yukon.head import main as main
