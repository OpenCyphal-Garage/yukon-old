# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import sys
import typing
import functools
import pyuavcan
from org_uavcan_yukon.io.frame import Frame_0_1 as Frame
from org_uavcan_yukon.io.iface.transport import Config_0_1 as Config


class Transport:
    NAME: str
    """
    Lowercase name of the transport that is also used in DCS unions: "udp", "serial", "can", etc.
    """

    @staticmethod
    def select_by_dcs_union(selector: pyuavcan.dsdl.CompositeObject) -> typing.Type[Transport]:
        for des in pyuavcan.util.iter_descendants(Transport):
            if getattr(selector, des.NAME, None):
                return des
        raise TypeError(f"No matching transport for {selector}")

    @staticmethod
    @functools.lru_cache(None)
    def select_by_type(selector: typing.Type[pyuavcan.transport.Transport]) -> typing.Type[Transport]:
        name = selector.__name__.lower()
        for des in pyuavcan.util.iter_descendants(Transport):
            if name.startswith(des.NAME):
                return des
        raise TypeError(f"No matching transport for {selector}")

    @staticmethod
    def get_capture_payload_size(cap: pyuavcan.transport.Capture) -> int:
        raise NotImplementedError

    @staticmethod
    def to_dcs_capture(cap: pyuavcan.transport.Capture) -> Frame:
        raise NotImplementedError

    @staticmethod
    def from_dcs_capture(ts: pyuavcan.transport.Timestamp, fr: Frame) -> pyuavcan.transport.Capture:
        raise NotImplementedError

    @staticmethod
    def from_dcs_config(cfg: Config) -> pyuavcan.transport.Transport:
        raise NotImplementedError


pyuavcan.util.import_submodules(sys.modules[__name__])
