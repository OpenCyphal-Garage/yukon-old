#!/usr/bin/env python3
#
# Copyright (C) 2021 UAVCAN Consortium
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import logging
import setuptools
import distutils.command.build_py
from pathlib import Path


PACKAGE_NAME = "yukon"
DSDL_SOURCE_ROOT = Path(__file__).resolve().parent / PACKAGE_NAME / "dsdl_src"


# noinspection PyUnresolvedReferences
class BuildPy(distutils.command.build_py.build_py):
    """Transpiles DSDL sources into Python packages."""

    def run(self):
        destination = Path(self.build_lib, PACKAGE_NAME, ".compiled_dsdl").resolve()
        print("DSDL transpilation output directory:", destination)
        if not self.dry_run:
            from pyuavcan.dsdl import generate_package

            generate_package(
                DSDL_SOURCE_ROOT / "public_regulated_data_types" / "uavcan",
                lookup_directories=[],
                output_directory=destination,
            )
            generate_package(
                DSDL_SOURCE_ROOT / "public_unregulated_data_types" / "org_uavcan_yukon",
                lookup_directories=[
                    DSDL_SOURCE_ROOT / "public_regulated_data_types" / "uavcan",
                ],
                output_directory=destination,
            )

        super().run()


logging.basicConfig(level=logging.INFO, format="%(levelname)-3.3s %(name)s: %(message)s")

setuptools.setup(
    cmdclass={"build_py": BuildPy},
)
