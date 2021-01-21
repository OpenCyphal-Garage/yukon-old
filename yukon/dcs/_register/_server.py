# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import os
import typing
from pathlib import Path
import logging
import pyuavcan
from uavcan.register import Access_1_0 as Access, Value_1_0 as Value


AssignableType = typing.Union[
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

_logger = logging.getLogger(__name__)


class ConflictError(ValueError):
    pass


class RegisterServer:
    def __init__(
        self,
        presentation: pyuavcan.presentation.Presentation,
        database_file: typing.Optional[typing.Union[str, Path]] = None,
        *,
        create_from_env: typing.Union[typing.Dict[str, str], bool] = True,
        set_from_env: typing.Union[typing.Dict[str, str], bool] = True,
    ) -> None:
        self._srv_access = presentation.get_server_with_fixed_service_id(Access)
        self._hooks: typing.List[typing.Callable[[str, Value], typing.Optional[Value]]] = [self.set]

        self._db = _Database(database_file)

    def start(self) -> None:
        self._srv_access.serve_in_background(self._on_request)

    def close(self) -> None:
        self._srv_access.close()

    def add_access_hook(self, hook: typing.Callable[[str, Value], typing.Optional[Value]]) -> None:
        """
        The hooks are invoked when the server receives a ``uavcan.register.Access`` request.
        All hooks are invoked sequentially starting with the last registered one (i.e., last added takes precedence).
        The first hook to return a value (instead of None) terminates the loop and makes the server return the value.
        If all hooks return None, the server will simply execute :meth:`set` and send the result back.
        """
        self._hooks.append(hook)

    def keys(self) -> typing.Iterable[str]:
        raise NotImplementedError

    def get(self, name: str) -> typing.Optional[Value]:
        """
        Returns None if the register does not exist.
        """
        raise NotImplementedError

    def set(self, name: str, value: AssignableType) -> Value:
        """
        If the value is empty or if the register does not exist, this is a no-op and the return value is empty.

        If the register exists and the type of the value is matching or can be converted to its type, the value
        is converted, assigned, and the resulting value returned.

        If the register exists but the value cannot be converted to the correct type, the old value is retained
        and returned.
        """
        raise NotImplementedError

    def create(self, name: str, value: Value, *, flags: Flags) -> None:
        """
        Creates a new register if it doesn't exist.
        If the register already exists and its name, value, and flags match the arguments, does nothing
        (the method is thus idempotent).
        If the register already exists and any of its parameters are different, a :class:`ConflictError` is raised.
        If the value is empty, a :class:`ValueError` is raised.
        """
        raise NotImplementedError

    def clear(self) -> None:
        """
        Erase all registers. Calling :meth:`set_from_environment_variables` afterwards might be sensible.
        """
        raise NotImplementedError

    def __getitem__(self, item: str) -> Value:
        """
        Like :meth:`get`, but if the register is missing it raises :class:`KeyError` instead of returning None.
        """
        out = self.get(item)
        if out is None:
            raise KeyError(item)
        return out

    async def _on_request(
        self, request: Access.Request, meta: pyuavcan.presentation.ServiceRequestMetadata
    ) -> Access.Response:
        pass
