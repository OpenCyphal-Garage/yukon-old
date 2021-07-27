# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import os
import sys
import typing
from pathlib import Path


AnyPath = typing.Union[str, Path]


class AppDirs:
    @property
    def root(self) -> Path:
        user = Path("~").expanduser()
        if sys.platform.startswith("win"):
            root = os.environ.get("APPDATA", user)
            return _prepare(Path(root, "UAVCAN", "Yukon"))

        if sys.platform.startswith("darwin"):
            return _prepare(user / "Library" / "Application Support" / "UAVCAN" / "Yukon")

        root = Path(os.environ.get("XDG_CONFIG_HOME", user / ".config"))
        return _prepare(root / "uavcan" / "yukon")

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
