# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import sys
import pathlib

TEST_ROOT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT_DIR = TEST_ROOT_DIR.parent
BUILD_LIB_DIR = PROJECT_ROOT_DIR / "build" / "lib"
COMPILED_DIR = BUILD_LIB_DIR / "yukon" / ".compiled"

# The package has to be built before the test suite can be executed.
sys.path.insert(0, str(BUILD_LIB_DIR))
sys.path.insert(0, str(COMPILED_DIR))
