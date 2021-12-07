# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import os
import sys
import typing
import importlib.metadata
import coloredlogs
from pathlib import Path


# pyproject.toml is the central place where all project metadata is kept. Only there.
# The package cannot be used from sources -- it has to be built beforehand.
META = importlib.metadata.metadata("yukon")
__version__ = META["version"]
__version_info__: typing.Tuple[int, ...] = tuple(map(int, __version__.split(".")[:3]))
__author__ = META["author"]
__email__ = META["author-email"]
__copyright__ = f"Copyright (c) 2021 {__author__} <{__email__}>"
__license__ = "MIT"


coloredlogs.install(level=os.getenv("YUKON_LOGLEVEL", "WARNING"))

# DSDL packages are pre-compiled when the package is built, so we do not need to compile our dependencies at runtime.
sys.path.insert(0, str(Path(__file__).resolve().parent / ".compiled"))
