# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
from typing import Optional, Dict, Tuple, List
from . import Value


def parse_environment_variables(env: Optional[Dict[str, str]] = None) -> List[Tuple[str, Value]]:
    """
    Given a list of environment variables, generates pairs of (name, :class:`Value`).
    A register name is mapped to the environment variable name as follows:

    >>> name = 'm.motor.flux_linkage'
    >>> ty = 'real32'
    >>> (name + "." + ty).upper().replace(".", "_" * 2)  # Name mapping rule.
    'M__MOTOR__FLUX_LINKAGE__REAL32'

    Where ``ty`` is the name of the value option from ``uavcan.register.Value``, like ``bit``, ``integer8``, etc.
    Array items are separated using the standard path separator (e.g., colon or semicolon, depending on platform).
    Environment variables that contain invalid values or named incorrectly are simply ignored.
    """
    pass
