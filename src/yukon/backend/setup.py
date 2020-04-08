#!/usr/bin/env python3
#
# Copyright (C) 2020  UAVCAN Development Team  <uavcan.org>
#               2020  dronesolutions.io. All rights reserved.
# This software is distributed under the terms of the MIT License.
#

import os
import sys
import setuptools

from typing import Dict

if int(setuptools.__version__.split('.')[0]) < 30:
    print('A newer version of setuptools is required. The current version does not support declarative config.',
          file=sys.stderr)
    sys.exit(1)

version = {}  # type: Dict
with open(os.path.dirname(os.path.realpath(__file__)) + '/src/api/version.py') as fp:
    exec(fp.read(), version)

setuptools.setup(version=version['__version__'],
                 package_data={'': ['*.ini']})
