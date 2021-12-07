# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import sys
from pathlib import Path
import nox

if sys.version_info < (3, 10):
    raise RuntimeError("A newer version of Python is required")

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIRS = [
    ROOT_DIR / "tests",
    ROOT_DIR / "yukon",
]


@nox.session(python=False)
def clean(session):
    import shutil

    wildcards = [
        "dist",
        "build",
        "html*",
        ".coverage*",
        ".*cache",
        ".*compiled",
        "*.egg-info",
        "*.log",
        "*.tmp",
        ".nox",
    ]
    for w in wildcards:
        for f in Path.cwd().glob(w):
            session.log(f"Removing: {f}")
            shutil.rmtree(f, ignore_errors=True)


@nox.session(reuse_venv=True)
def test(session):
    session.install(
        "pytest         ~= 6.2",
        "pytest-asyncio ~= 0.16",
    )
    session.run(sys.executable, ROOT_DIR / "setup.py", "build")
    session.install(f"-e{ROOT_DIR}")

    if sys.platform.startswith("linux"):
        # Enable packet capture for the Python executable. This is necessary for testing the UDP capture capability.
        # It can't be done from within the test suite because it has to be done before the interpreter is started.
        session.run("sudo", "setcap", "cap_net_raw+eip", str(Path(session.bin, "python").resolve()), external=True)

    env = {
        "PYTHONASYNCIODEBUG": "1",
    }
    session.run("pytest", *session.posargs, env=env)


@nox.session(reuse_venv=True)
def static_analysis(session):
    session.run(sys.executable, ROOT_DIR / "setup.py", "build")
    session.install(
        "mypy   ~= 0.910",
        "pylint ~= 2.12",
        "black  ~= 21.12b0",
    )
    session.install(f"-e{ROOT_DIR}")
    session.run("mypy", "--strict", *map(str, SRC_DIRS))
    session.run("pylint", *map(str, SRC_DIRS))
    session.run("black", "--check", str(ROOT_DIR))
