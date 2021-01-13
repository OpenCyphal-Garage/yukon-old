# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
from pathlib import Path
import click


AnyPath = typing.Union[str, Path]

PACKAGE_ROOT = Path(__file__).resolve().parent.parent

_DSDL_ROOT = PACKAGE_ROOT / "dsdl"
DSDL_NAMESPACES = {
    "org_uavcan_yukon": _DSDL_ROOT / "org_uavcan_yukon",
    "uavcan": _DSDL_ROOT / "public_regulated_data_types" / "uavcan",
    "reg": _DSDL_ROOT / "public_regulated_data_types" / "reg",
}


class AppDirs:
    @property
    def root(self) -> Path:
        import yukon

        return _prepare(click.get_app_dir(yukon.__name__))

    @property
    def log(self) -> Path:
        return _prepare(self.root / "log")

    @property
    def version_specific(self) -> Path:
        from yukon import __version__

        return _prepare(self.root / f"v{__version__}")

    @property
    def compiled_dsdl(self) -> Path:
        return _prepare(self.version_specific / "compiled_dsdl")


APP_DIRS = AppDirs()


def _prepare(directory: AnyPath) -> Path:
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    return directory
