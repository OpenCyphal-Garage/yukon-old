#!/usr/bin/env python3
#
# Copyright (C) 2020  UAVCAN Development Team  <uavcan.org>
#               2020  dronesolutions.io. All rights reserved.
# This software is distributed under the terms of the MIT License.
#

import os
import setuptools

from typing import Dict

os.chdir(os.path.abspath(os.path.dirname(__file__)))

if int(setuptools.__version__.split('.')[0]) < 30:
    raise Exception('A newer version of setuptools is required. '
                    'The current version does not support declarative config.')

version = {}  # type: Dict
with open('src/api/version.py') as fp:
    exec(fp.read(), version)

setuptools.setup(version=version['__version__'],
                 install_requires=['quart', 'quart_cors', 'typing'],
                 package_data={'': ['*.ini']})
