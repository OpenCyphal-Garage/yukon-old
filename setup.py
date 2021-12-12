#!python
# Copyright (C) 2021 UAVCAN Consortium
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>
# type: ignore

import setuptools
import distutils.command.build_py
from pathlib import Path


PACKAGE_NAME = "yukon"
PROJECT_ROOT = Path(__file__).resolve().parent
COMPILED_DIR = PROJECT_ROOT / PACKAGE_NAME / "_compiled"


# noinspection PyUnresolvedReferences
class BuildPy(distutils.command.build_py.build_py):
    def run(self):
        if not self.dry_run:
            from pyuavcan.dsdl import compile_all

            compile_all(
                [
                    PROJECT_ROOT / "deps" / "public_regulated_data_types" / "uavcan",
                    PROJECT_ROOT / "dsdl" / "org_uavcan_yukon",
                ],
                COMPILED_DIR,
            )
        super().run()


if __name__ == "__main__":
    # noinspection PyTypeChecker
    setuptools.setup(
        cmdclass={"build_py": BuildPy},
    )
