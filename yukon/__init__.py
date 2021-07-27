# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import os
import sys
import typing
import logging
from pathlib import Path

__version__: str = (Path(__file__).parent / "VERSION").read_text().strip()
__version_info__: typing.Tuple[int, ...] = tuple(map(int, __version__.split(".")[:3]))
__author__ = "UAVCAN Consortium"
__email__ = "consortium@uavcan.org"
__copyright__ = f"Copyright (c) 2021 {__author__} <{__email__}>"
__license__ = "MIT"


if sys.version_info < (3, 9):  # pragma: no cover
    raise RuntimeError("A newer version of Python is required")


logging.basicConfig(
    stream=sys.stderr,
    level=os.getenv("YUKON_LOGLEVEL", "WARNING"),
    format="%(asctime)s %(process)07d %(levelname)-3.3s: %(name)s: %(message)s",
)

# DSDL packages are pre-compiled when the package is built, so we do not need to compile our dependencies at runtime.
sys.path.insert(0, str(Path(__file__).resolve().parent / ".compiled"))
