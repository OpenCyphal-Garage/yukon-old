#!/usr/bin/env python3
# Copyright (C) 2021 UAVCAN Consortium
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>
# type: ignore

import toml
import setuptools
import distutils.command.build_py
from pathlib import Path


PACKAGE_NAME = "yukon"
PROJECT_ROOT = Path(__file__).resolve().parent

meta = toml.load(PROJECT_ROOT / "pyproject.toml")

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
                Path(self.build_lib, PACKAGE_NAME, ".compiled").resolve(),
            )
        super().run()


if __name__ == "__main__":
    # noinspection PyTypeChecker
    setuptools.setup(
        name=meta["project"]["name"],
        version=meta["project"]["version"],
        description=meta["project"]["description"],
        cmdclass={"build_py": BuildPy},
        packages=setuptools.find_packages(str(PROJECT_ROOT), include=("yukon", "yukon.*")),
        package_data={"yukon": ["*"]},
        include_package_data=True,
        zip_safe=False,
    )
