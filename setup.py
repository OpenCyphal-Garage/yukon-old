#!/usr/bin/env python3
# Copyright (C) 2021 UAVCAN Consortium
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>
# type: ignore

import setuptools
import distutils.command.build_py
from pathlib import Path


PACKAGE_NAME = "yukon"
DSDL_SOURCE_ROOT = Path(__file__).resolve().parent / PACKAGE_NAME / "dsdl_src"


# noinspection PyUnresolvedReferences
class BuildPy(distutils.command.build_py.build_py):
    def run(self):
        if not self.dry_run:
            from pyuavcan.dsdl import compile_all

            compile_all(
                [
                    DSDL_SOURCE_ROOT / "public_regulated_data_types" / "uavcan",
                    DSDL_SOURCE_ROOT / "public_unregulated_data_types" / "org_uavcan_yukon",
                ],
                Path(self.build_lib, PACKAGE_NAME, ".compiled").resolve(),
            )
        super().run()


# noinspection PyTypeChecker
setuptools.setup(
    cmdclass={"build_py": BuildPy},
)
