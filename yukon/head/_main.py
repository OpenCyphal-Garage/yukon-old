# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import os
import random
import logging
import asyncio
from typing import Callable, Any
import threading
import dearpygui.dearpygui as dpg
import pyuavcan
import pyuavcan.application
from pyuavcan.application import NodeInfo
from uavcan.node import Version_1


def main() -> int:
    _configure()
    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()
    dpg.configure_app(docking=True, docking_space=True)

    with dpg.window(label="Example Window"):
        dpg.add_text("Hello world")
        dpg.add_button(label="Save", callback=lambda: print("SAVE"))
        dpg.add_input_text(label="string")
        dpg.add_slider_float(label="float")

    dpg.show_viewport()

    stop = False
    thread_dcs = threading.Thread(target=asyncio.run, args=(_run_dcs(lambda: stop),), name="dcs")
    try:
        thread_dcs.start()
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
    finally:
        stop = True
        thread_dcs.join(10.0)
        dpg.destroy_context()

    return 0


async def _run_dcs(should_terminate: Callable[[], bool]) -> None:
    from yukon import __version_info__

    node = pyuavcan.application.make_node(
        NodeInfo(
            software_version=Version_1(*__version_info__[:2]),
            name="org.uavcan.yukon.head",
        )
    )
    try:
        if node.id is None:
            raise ValueError("DCS transport configuration error: node cannot be anonymous")
        node.start()
        while not should_terminate():
            await asyncio.sleep(1.0)
    finally:
        node.close()


def _configure() -> None:
    # This logic is questionable, will need to review later.
    def put(name: str, value: Any) -> None:
        _logger.info("%s= %r", name.ljust(30), value)
        os.putenv(name, str(value))

    put("UAVCAN__UDP__IFACE", f"127.{random.getrandbits(7)}.0.0")
    put("UAVCAN__NODE__ID", 0)


_logger = logging.getLogger(__name__)
