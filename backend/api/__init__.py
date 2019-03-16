#
# Copyright (C) 2019  UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
#

import sys
from .version import __version__, __license__
from . import app

if sys.version_info[:2] < (3, 7):   # pragma: no cover
    print('A newer version of Python is required', file=sys.stderr)
    sys.exit(1)
