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
        return Value(bit=Bit(s))
    if all(isinstance(x, int) for x in s):
        return Value(natural64=Natural64(s)) if all(x >= 0 for x in s) else Value(integer64=Integer64(s))
    if all(isinstance(x, float) for x in s):
        return Value(real64=Real64(s))

    raise ValueError(f"Don't know how to convert {s!r} into {Value}")  # pragma: no cover


def _get_option_name(x: Value) -> str:
    for n in VALUE_OPTION_NAMES:
        if get_attribute(x, n):
            return n
    raise TypeError(f"Invalid value: {x!r}; expected option names: {VALUE_OPTION_NAMES}")  # pragma: no cover


def _unittest_strictify() -> None:
    import pytest

    v = Value(string=String("abc"))
    assert v is _strictify(v)  # Transparency.

    assert list(_strictify(+1).natural64.value) == [+1]
    assert list(_strictify(-1).integer64.value) == [-1]
    assert list(_strictify(1.1).real64.value) == [pytest.approx(1.1)]
    assert list(_strictify(True).bit.value) == [True]
    assert _strictify([]).empty

    assert _strictify("Hello").string.value.tobytes().decode() == "Hello"
    assert _strictify(b"Hello").unstructured.value.tobytes() == b"Hello"


def _unittest_convert() -> None:
    import pytest

    q = Value

    def _once(a: q, b: q) -> q:
        c = convert(a, b)
        assert c
        return c

    assert _once(q(), q()).empty
    assert _once(q(), q(string=String("Hello"))).empty
    assert _once(q(string=String("A")), q(string=String("B"))).string.value.tobytes().decode() == "B"
    assert _once(q(string=String("A")), q(unstructured=Unstructured(b"B"))).string.value.tobytes().decode() == "B"
    assert list(_once(q(natural16=Natural16([1, 2])), q(natural64=Natural64([1, 2]))).natural16.value) == [1, 2]

    # Dimensionality mismatch.
    assert None is convert(q(integer16=Integer16([1, 2, 3])), q(integer16=Integer16([1, 2])))

    assert list(_once(q(bit=Bit([False, False])), q(integer32=Integer32([-1, 0]))).bit.value) == [True, False]
    assert list(_once(q(integer8=Integer8([0, 1])), q(real64=Real64([3.3, 6.4]))).integer8.value) == [3, 6]
    assert list(_once(q(integer16=Integer16([0, 1])), q(real64=Real64([3.3, 6.4]))).integer16.value) == [3, 6]
    assert list(_once(q(integer32=Integer32([0, 1])), q(real64=Real64([3.3, 6.4]))).integer32.value) == [3, 6]
    assert list(_once(q(integer64=Integer64([0, 1])), q(real64=Real64([3.3, 6.4]))).integer64.value) == [3, 6]
    assert list(_once(q(natural8=Natural8([0, 1])), q(real64=Real64([3.3, 6.4]))).natural8.value) == [3, 6]
    assert list(_once(q(natural16=Natural16([0, 1])), q(real64=Real64([3.3, 6.4]))).natural16.value) == [3, 6]
    assert list(_once(q(natural32=Natural32([0, 1])), q(real64=Real64([3.3, 6.4]))).natural32.value) == [3, 6]
    assert list(_once(q(natural64=Natural64([0, 1])), q(real64=Real64([3.3, 6.4]))).natural64.value) == [3, 6]
    assert list(_once(q(real16=Real16([0])), q(bit=Bit([True]))).real16.value) == [pytest.approx(1.0)]
    assert list(_once(q(real32=Real32([0])), q(bit=Bit([True]))).real32.value) == [pytest.approx(1.0)]
    assert list(_once(q(real64=Real64([0])), q(bit=Bit([True]))).real64.value) == [pytest.approx(1.0)]
