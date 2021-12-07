#!python
# Copyright (C) 2021 UAVCAN Consortium
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>
# type: ignore

import re
import setuptools
import distutils.command.build_py
from pathlib import Path


PACKAGE_NAME = "yukon"
PROJECT_ROOT = Path(__file__).resolve().parent

# We can't use the normal toml parser because can't rely on non-trivial external dependencies in setup.py.
with open(PROJECT_ROOT / "pyproject.toml", "r") as f:
    pyp = f.read()
    version = re.findall(r"""version\s*=\s*['"]([\w\d._]+)['"]""", pyp)[0].strip()
    description = re.findall(r'description\s*=\s*"([^\r\n]+)"', pyp)[0].strip()


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
        name=PACKAGE_NAME,
        version=version,
        description=description,
        cmdclass={"build_py": BuildPy},
        packages=setuptools.find_packages(str(PROJECT_ROOT), include=("yukon", "yukon.*")),
        package_data={"yukon": ["*"]},
        include_package_data=True,
        zip_safe=False,
    )
