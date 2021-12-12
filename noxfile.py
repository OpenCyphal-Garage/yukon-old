# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import sys
from pathlib import Path
import nox


ROOT_DIR = Path(__file__).resolve().parent
SRC_DIRS = [
    ROOT_DIR / "tests",
    ROOT_DIR / "yukon",
]

nox.options.error_on_external_run = True


@nox.session(python=False)
def clean(session):
    import shutil

    wildcards = [
        "dist",
        "build",
        "html*",
        ".coverage*",
        ".*cache",
        "*.egg-info",
        "*.log",
        "*.tmp",
        ".nox",
        "*/_compiled/",
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
    setup(session)
    if sys.platform.startswith("linux"):
        # Enable packet capture for the Python executable. This is necessary for testing the UDP capture capability.
        # It can't be done from within the test suite because it has to be done before the interpreter is started.
        session.run("sudo", "setcap", "cap_net_raw+eip", str(Path(session.bin, "python").resolve()), external=True)
    # Change UAVCAN__UDP__IFACE to use a different transport for the DCS (e.g., UAVCAN/serial over TCP with a broker).
    env = {
        "YUKON__DCS__HEAD_NODE_ID": "0",
        "UAVCAN__UDP__IFACE": "127.42.0.0",
        "PYTHONASYNCIODEBUG": "1",
    }
    session.run("pytest", "-x", *session.posargs, env=env)


@nox.session(reuse_venv=True)
def static_analysis(session):
    session.install(
        "mypy   ~= 0.910",
        "pylint ~= 2.12",
        "black  ~= 21.12b0",
    )
    setup(session)
    session.run("mypy", "--strict", *map(str, SRC_DIRS))
    session.run("pylint", *map(str, SRC_DIRS))
    session.run("black", "--check", str(ROOT_DIR))


def setup(session):
    session.install("pyuavcan")  # Needed for DSDL transcompilation: https://github.com/UAVCAN/pyuavcan/issues/110
    session.run("python", str(ROOT_DIR / "setup.py"), "build")
    session.install(f"-e{ROOT_DIR}")
