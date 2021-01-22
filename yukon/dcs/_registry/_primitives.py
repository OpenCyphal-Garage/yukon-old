# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import typing
import numpy
from pyuavcan.dsdl import get_attribute
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
These types can be automatically converted to a ``uavcan.register.Value``.
"""


def parse_environment_variables(env: typing.Dict[str, str]) -> typing.Iterable[typing.Tuple[str, Value]]:
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


def convert(to: Value, source: RelaxedValue) -> typing.Optional[Value]:
    """
    Converts the source into the type of destination.
    Only the type information from the destination is used; its value is ignored.
    If such conversion is not possible, None is returned.
    Notice that per Specification, such implicit conversion is entirely optional;
    for instance, embedded systems are unlikely to implement this.
    """
    opt_to = _get_option_name(to)
    out = _do_convert(to, _strictify(source))
    assert out is None or _get_option_name(out) == opt_to
    return out


def _do_convert(to: Value, s: Value) -> typing.Optional[Value]:
    """
    This is a bit rough around the edges; consider it to be an MVP.
    """
    if to.empty or s.empty:  # Everything is convertible to empty, and empty is convertible to everything.
        return to
    if (to.string and s.string) or (to.unstructured and s.unstructured):
        return s
    if to.string and s.unstructured:
        return Value(string=String(s.unstructured.value))
    if to.unstructured and s.string:
        return Value(unstructured=Unstructured(s.string.value))

    opt_to, opt_s = _get_option_name(to), _get_option_name(s)
    val_to: numpy.ndarray = get_attribute(to, opt_to).value
    val_s: numpy.ndarray = get_attribute(s, opt_s).value
    if len(val_to) != len(val_s):
        return None  # Dimensionality mismatch.
    # At this point it is known that both values are of the same dimension.
    if opt_to == opt_s:  # Also same scalar type -- no further checks needed.
        return s
    # fmt: off
    if to.bit:    return Value(bit=Bit([x != 0 for x in val_s]))
    if to.real16: return Value(real16=Real16(val_s))
    if to.real32: return Value(real32=Real32(val_s))
    if to.real64: return Value(real64=Real64(val_s))
    # fmt: on
    val_s_int = [round(x) for x in val_s]
    del val_s
    # fmt: off
    if to.integer8:  return Value(integer8=Integer8(val_s_int))
    if to.integer16: return Value(integer16=Integer16(val_s_int))
    if to.integer32: return Value(integer32=Integer32(val_s_int))
    if to.integer64: return Value(integer64=Integer64(val_s_int))
    if to.natural8:  return Value(natural8=Natural8(val_s_int))
    if to.natural16: return Value(natural16=Natural16(val_s_int))
    if to.natural32: return Value(natural32=Natural32(val_s_int))
    if to.natural64: return Value(natural64=Natural64(val_s_int))
    # fmt: on
    assert False


def _strictify(s: RelaxedValue) -> Value:
    if isinstance(s, Value):
        return s
    if isinstance(s, (bool, int, float)):
        return _strictify([s])
    if isinstance(s, str):
        return Value(string=String(s))
    if isinstance(s, bytes):
        return Value(unstructured=Unstructured(s))

    s = list(s)
    if not s:
        return Value()  # Empty list generalized into Value.empty.
    if all(isinstance(x, bool) for x in s):
        return Value(bit=s)
    if all(isinstance(x, int) for x in s):
        return Value(natural64=s) if all(x >= 0 for x in s) else Value(integer64=s)
    if all(isinstance(x, float) for x in s):
        return Value(real64=s)

    raise ValueError(f"Don't know how to convert {s!r} into {Value}")


def _get_option_name(x: Value) -> str:
    for n in VALUE_OPTION_NAMES:
        if get_attribute(x, n):
            return n
    raise TypeError(f"Invalid value: {x!r}; expected option names: {VALUE_OPTION_NAMES}")  # pragma: no cover


def _unittest_strictify() -> None:
    pass
