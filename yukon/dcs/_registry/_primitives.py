# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import typing
from . import Value, String, Unstructured, Bit
from . import Integer8, Integer16, Integer32, Integer64
from . import Natural8, Natural16, Natural32, Natural64
from . import Real16, Real32, Real64


VALUE_OPTION_NAMES = [x for x in dir(Value) if not x.startswith("_")]


RelaxedValue = typing.Union[
    Value,
    str,
    bytes,
    bool,
    int,
    float,
    typing.Iterable[bool],
    typing.Iterable[int],
    typing.Iterable[float],
]
"""
These types can be automatically converted to a ``uavcan.register.Value``:

- ``str``             -> ``string``
- ``bytes``           -> ``unstructured``
- ``bool``            -> ``bit[1]``
- ``int``             -> ``integerXX[1]``
- ``float``           -> ``realXX[1]``
- ``Iterable[bool]``  -> ``bit[]``
- ``Iterable[int]``   -> ``integerXX[]``
- ``Iterable[float]`` -> ``realXX[]``
"""


def assign(target: Value, source: RelaxedValue) -> bool:
    if isinstance(source, (bool, int, float)):  # Scalar generalization.
        return assign(target, [source])

    if isinstance(source, str):
        pr = String(source)
    elif isinstance(source, bytes):
        pr = Unstructured(source)
    elif not isinstance(source, Value):
        pass
