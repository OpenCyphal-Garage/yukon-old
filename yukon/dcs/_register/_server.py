# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
from fnmatch import fnmatchcase
import typing
from pathlib import Path
import logging
import pyuavcan
from uavcan.register import Access_1_0 as Access
from ._storage import Storage, Flags, Value
from ._primitives import AssignableType, assign


_logger = logging.getLogger(__name__)


class ConflictError(ValueError):
    pass


class RegisterServer:
    def __init__(
        self,
        presentation: pyuavcan.presentation.Presentation,
        storage_file: typing.Optional[typing.Union[str, Path]] = None,
    ) -> None:
        self._srv_access = presentation.get_server_with_fixed_service_id(Access)
        self._hooks: typing.List[typing.Callable[[str, Value], typing.Optional[Value]]] = []
        self._storage = Storage(storage_file)
        self.add_access_hook(self.set)  # Last hook, lowest precedence, last resort.

    def start(self) -> None:
        """
        Starts the ``uavcan.register.Access`` server. All other functionality is available regardless of this.
        """
        self._srv_access.serve_in_background(self._on_request)

    def close(self) -> None:
        self._srv_access.close()
        self._storage.close()

    def add_access_hook(self, hook: typing.Callable[[str, Value], typing.Optional[Value]]) -> None:
        """
        The hooks are invoked when the server receives a ``uavcan.register.Access`` request.
        All hooks are invoked sequentially starting with the last registered one (i.e., last added takes precedence).
        The first hook to return a value (instead of None) terminates the loop and makes the server return the value.
        If all hooks return None, the server will simply execute :meth:`set` and send the result back.
        """
        self._hooks.append(hook)

    def keys(self) -> typing.List[str]:
        """
        >>> from uavcan.primitive.array import Bit_1_0
        >>> rs = RegisterServer(_make_loopback())
        >>> rs.create("b", Value(bit=Bit_1_0([True, False])))
        >>> rs.create("a", Value(bit=Bit_1_0()))
        >>> rs.keys()  # Sorted lexicographically.
        ['a', 'b']
        """
        return self._storage.get_names()

    def get(self, name: str) -> typing.Optional[Value]:
        """
        >>> from uavcan.primitive.array import Bit_1_0
        >>> rs = RegisterServer(_make_loopback())
        >>> rs.get("foo") is None  # No such register --> None.
        True
        >>> rs.create("foo", Value(bit=Bit_1_0([True, False])))
        >>> value = rs.get("foo")
        >>> not value.empty                         # Detect the type by querying the union fields.
        True
        >>> not value.string                        # etc...
        True
        >>> value.bit.value[0], value.bit.value[1]  # The value is a standard NumPy array.
        (True, False)
        """
        val_flags = self._storage.get(name)
        if val_flags is None:
            return None
        val, _ = val_flags
        return val

    def set(self, name: str, value: AssignableType) -> Value:
        """
        If the register exists and the type of the value is matching or can be converted to the register's type,
        the value is assigned and the resulting converted value is returned.

        Observe that the mutability/persistence flags bear no relevance here because they only affect the RPC-service.

        :raises: :class:`KeyError` if the register does not exist.
                 :class:`ConflictError` if the register exists but the value cannot be converted to its type.
        """
        val_flags = self._storage.get(name)
        if not val_flags:
            raise KeyError(name)
        assignee, flags = val_flags
        if not assign(assignee, value):
            raise ConflictError(f"Cannot assign {assignee!r} from {value!r}")
        self._storage.set(name, assignee, flags)
        return assignee

    def create(self, name: str, value: Value, *, mutable: bool = True, persistent: bool = True) -> None:
        """
        If the register exists, behaves like :meth:`set` and the flags are ignored. Otherwise it is created.

        :raises: :class:`ValueError` if the name or value are empty.
        """
        if not name or value.empty:
            raise ValueError("Cannot create an empty register")
        try:
            self.set(name, value)
        except KeyError:
            self._storage.set(name, value, Flags(mutable=mutable, persistent=persistent))

    def delete(self, wildcard: str) -> None:
        """
        Remove all registers that match the specified wildcard. Matching is case-sensitive.

        >>> from uavcan.primitive.array import Bit_1_0
        >>> rs = RegisterServer(_make_loopback())
        >>> rs.create("foo.bar", Value(bit=Bit_1_0()))
        >>> rs.create("foo.baz", Value(bit=Bit_1_0()))
        >>> rs.create("bar.bar", Value(bit=Bit_1_0()))
        >>> rs.delete("foo.*")
        >>> rs.keys()
        ['bar_bar']
        """
        names = [n for n in self.keys() if fnmatchcase(n, wildcard)]
        _logger.debug("Deleting %d registers matching %r: %r", len(names), wildcard, names)
        self._storage.delete(names)

    async def _on_request(
        self, request: Access.Request, meta: pyuavcan.presentation.ServiceRequestMetadata
    ) -> Access.Response:
        pass

    def __getitem__(self, item: str) -> Value:
        """
        Like :meth:`get`, but if the register is missing it raises :class:`KeyError` instead of returning None.

        >>> from uavcan.primitive.array import Bit_1_0
        >>> rs = RegisterServer(_make_loopback())
        >>> rs["foo"]
        Traceback (most recent call last):
        ...
        KeyError: 'foo'
        >>> rs.create("foo", Value(bit=Bit_1_0([True])))
        >>> rs["foo"].bit.value[0]
        True
        """
        out = self.get(item)
        if out is None:
            raise KeyError(item)
        return out

    def __iter__(self) -> typing.Iterator[str]:
        """
        >>> from uavcan.primitive.array import Bit_1_0
        >>> rs = RegisterServer(_make_loopback())
        >>> rs.create("b", Value(bit=Bit_1_0()))
        >>> rs.create("a", Value(bit=Bit_1_0()))
        >>> list(rs)
        ['a', 'b']
        """
        return iter(self.keys())

    def __repr__(self) -> str:
        return pyuavcan.util.repr_attributes(self, self._storage, self._srv_access)


def _make_loopback() -> pyuavcan.presentation.Presentation:
    """This is for testing only."""
    from pyuavcan.transport.loopback import LoopbackTransport

    return pyuavcan.presentation.Presentation(LoopbackTransport(1))
