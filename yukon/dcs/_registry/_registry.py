# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
from fnmatch import fnmatchcase
import typing
from pathlib import Path
import logging
import pyuavcan
from ._storage import Storage, Entry, Value
from ._primitives import RelaxedValue, assign


_logger = logging.getLogger(__name__)


class ConflictError(ValueError):
    pass


class MissingRegisterError(KeyError):
    pass


class Registry:
    def __init__(self, storage_file: typing.Optional[typing.Union[str, Path]] = None, immutable: bool = False) -> None:
        """
        :param storage_file: Where to read from and store to the registry data.
            The file will be created if it doesn't exist.
            If not provided, the registry will be kept in-memory, in which case :attr:`persistent` is False.
            If provided but the file is not writable, all registers will be marked immutable.

        :param immutable: Assume the storage to be immutable even if it is actually writable.
        """
        self._storage = Storage(storage_file, immutable=immutable)

    @property
    def mutable(self) -> bool:
        """
        Whether the storage can be modified at all.
        If not, every register will be reported as immutable when read regardless of its own mutability status.

        >>> rs = Registry()
        >>> rs.create("foo", Value(), mutable=True)     # Create a new register and make it mutable.
        >>> rs.get("foo").mutable                       # Confirm that it is read as mutable.
        True
        >>> rs = Registry(immutable=True)               # Force immutability of the storage.
        >>> rs.create("foo", Value(), mutable=True)     # Create a new register and make it mutable.
        >>> rs.get("foo").mutable                       # Reads back as immutable because the storage is immutable.
        False
        """
        return self._storage.mutable

    @property
    def persistent(self) -> bool:
        """True if the registry is stored on-disk, False if it is in-memory."""
        return self._storage.persistent

    def close(self) -> None:
        """Closes the file handles related to the storage."""
        self._storage.close()

    def keys(self) -> typing.List[str]:
        """
        >>> from uavcan.primitive.array import Bit_1_0
        >>> rs = Registry()
        >>> rs.create("b", Value(bit=Bit_1_0([True, False])))
        >>> rs.create("a", Value(bit=Bit_1_0()))
        >>> rs.keys()  # Sorted lexicographically.
        ['a', 'b']
        """
        return self._storage.get_names()

    def get(self, name: str) -> typing.Optional[Entry]:
        """
        >>> from uavcan.primitive.array import Bit_1_0
        >>> rs = Registry()
        >>> rs.get("foo") is None                       # No such register --> None.
        True
        >>> rs.create("foo", Value(bit=Bit_1_0([True, False])))
        >>> e = rs.get("foo")
        >>> not e.value.empty                           # Detect the type by querying the union fields.
        True
        >>> not e.value.string                          # etc...
        True
        >>> e.value.bit.value[0], e.value.bit.value[1]  # The value is a standard NumPy array.
        (True, False)
        """
        e = self._storage.get(name)
        if e is None:
            return None
        return Entry(e.value, mutable=e.mutable and self._storage.mutable)

    def set(self, name: str, value: RelaxedValue) -> Entry:
        """
        If the register exists and the type of the value is matching or can be converted to the register's type,
        the value is assigned and the resulting converted value is returned.

        :raises: :class:`MissingRegisterError` (subclass of :class:`KeyError`) if the register does not exist.
                 :class:`ConflictError` if the register exists but the value cannot be converted to its type.
        """
        e = self._storage.get(name)
        if not e:
            raise MissingRegisterError(name)
        if not assign(e.value, value):
            raise ConflictError(f"Cannot assign {e.value!r} from {value!r}")
        self._storage.set(name, e)
        return e

    def create(self, name: str, value: Value, *, mutable: bool = True) -> None:
        """
        If the register exists, behaves like :meth:`set` and the flags are ignored. Otherwise it is created.
        """
        try:
            self.set(name, value)
        except MissingRegisterError:
            self._storage.set(name, Entry(value, mutable=mutable))

    def delete(self, wildcard: str) -> None:
        """
        Remove all registers that match the specified wildcard. Matching is case-sensitive.

        >>> rs = Registry()
        >>> rs.create("foo.bar", Value())
        >>> rs.create("foo.baz", Value())
        >>> rs.create("zoo.bar", Value())
        >>> rs.delete("foo.*")
        >>> rs.keys()
        ['zoo_bar']
        """
        names = [n for n in self.keys() if fnmatchcase(n, wildcard)]
        _logger.debug("Deleting %d registers matching %r: %r", len(names), wildcard, names)
        self._storage.delete(names)

    def __getitem__(self, item: str) -> Entry:
        """
        Like :meth:`get`, but if the register is missing it raises :class:`MissingRegisterError`
        (subclass of :class:`KeyError`) instead of returning None.

        >>> from uavcan.primitive.array import Bit_1_0
        >>> rs = Registry()
        >>> rs["foo"]
        Traceback (most recent call last):
        ...
        MissingRegisterError: 'foo'
        >>> rs.create("foo", Value(bit=Bit_1_0([True])))
        >>> rs["foo"].value.bit.value[0]
        True
        """
        e = self.get(item)
        if e is None:
            raise MissingRegisterError(item)
        return e

    def __iter__(self) -> typing.Iterator[str]:
        """
        >>> rs = Registry()
        >>> rs.create("b", Value())
        >>> rs.create("a", Value())
        >>> list(rs)
        ['a', 'b']
        """
        return iter(self.keys())

    def __repr__(self) -> str:
        return pyuavcan.util.repr_attributes(self, self._storage)
