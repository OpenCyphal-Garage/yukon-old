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
DSDL_NAMESPACES = [
    PROJECT_ROOT / "deps" / "public_regulated_data_types" / "uavcan",
    PROJECT_ROOT / "dsdl" / "org_uavcan_yukon",
]


# noinspection PyUnresolvedReferences
class BuildPy(distutils.command.build_py.build_py):
    def run(self):
        if not self.dry_run:
            ts_input = max(x.stat().st_mtime for ns in DSDL_NAMESPACES for x in ns.rglob("*.uavcan"))
            ts_output = COMPILED_DIR.stat().st_mtime if COMPILED_DIR.is_dir() else 0.0
            if ts_input > ts_output:
                from pyuavcan.dsdl import compile_all

                print("Compiling DSDL:", list(map(str, DSDL_NAMESPACES)), " --> ", COMPILED_DIR)
                compile_all(DSDL_NAMESPACES, COMPILED_DIR)
                COMPILED_DIR.touch(exist_ok=True)
            else:
                print("DSDL compilation skipped: DSDL sources not modified")
        super().run()


if __name__ == "__main__":
    # noinspection PyTypeChecker
    setuptools.setup(
        cmdclass={"build_py": BuildPy},
    )
