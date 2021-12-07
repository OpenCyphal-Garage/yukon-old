# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import sys
import pathlib

TEST_ROOT_DIR = pathlib.Path(__file__).parent
PROJECT_ROOT_DIR = TEST_ROOT_DIR.parent
COMPILED_DIR = PROJECT_ROOT_DIR / "build" / "lib" / "yukon" / ".compiled"

sys.path.insert(0, str(PROJECT_ROOT_DIR))
sys.path.insert(0, str(COMPILED_DIR))
