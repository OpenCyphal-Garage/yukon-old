# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from __future__ import annotations
import typing
import dataclasses
from pathlib import Path
import logging
import sqlite3
import pyuavcan
from uavcan.register import Value_1_0 as Value


_TIMEOUT = 0.5
_LOCATION_VOLATILE = ":memory:"


@dataclasses.dataclass(frozen=True)
class Flags:
    mutable: bool
    persistent: bool


# noinspection SqlNoDataSourceInspection,SqlResolve
class Storage:
    """
    Register storage backend implementation.
    Supports either persistent on-disk single-file storage or volatile in-memory storage.
    """

    def __init__(self, location: typing.Optional[typing.Union[str, Path]] = None):
        """
        :param location: Either a path to the database file, or None. If None, the registry will be stored in memory.
        """
        loc = str(location or _LOCATION_VOLATILE).strip()
        self._db = sqlite3.connect(loc, timeout=_TIMEOUT)
        self._mutable = self._check_mutability()
        self._persistent = loc.lower() != _LOCATION_VOLATILE

        self._db.execute(
            r"""
            create table if not exists `registry` (
                `name`          varchar(255) not null unique primary key,
                `mutable`       boolean not null,
                `persistent`    boolean not null,
                `value`         blob not null,
                `ts`            time not null default current_timestamp
            )
            """
        )
        self._db.commit()

    @property
    def flags(self) -> Flags:
        """
        These flags are derived from the properties of the storage file.
        In-memory DB is reported as not persistent. A non-writeable DB is reported as immutable.
        """
        return Flags(mutable=self._mutable, persistent=self._persistent)

    def get_names(self) -> typing.List[str]:
        """
        :returns: List of all registers ordered lexicographically.
        """
        return [x for x, in self._db.execute(r"select name from registry order by name").fetchall()]

    def get_name_by_index(self, index: int) -> typing.Optional[str]:
        """
        :returns: Name of the register at the specified index or None if the index is out of range.
            The ordering is guaranteed to be stable while the set of registers is not modified.
        """
        try:
            # TODO: this is super inefficient, make a request instead.
            return self.get_names()[index]
        except IndexError:
            return None

    def get(self, name: str) -> typing.Optional[typing.Tuple[Value, Flags]]:
        """
        :returns: None if no such register is available.
        """
        res = self._db.execute(r"select mutable, persistent, value from registry where name = ?", (name,)).fetchone()
        if res is None:
            return None
        mutable, persistent, value = res
        assert isinstance(value, bytes)
        obj = pyuavcan.dsdl.deserialize(Value, [memoryview(value)])
        if obj is None:  # pragma: no cover
            _logger.warning(
                "Database: stored value of %r is not a valid serialized representation of %s: %r", name, Value, value
            )
        # If the entire DB is immutable, no point reporting a single register as mutable. Same for persistency.
        return obj, Flags(
            mutable=mutable and self.flags.mutable,
            persistent=persistent and self.flags.persistent,
        )

    def set(self, name: str, value: Value, flags: Flags) -> None:
        """
        If the register does not exist, it will be created.
        If exists, it will be overwritten unconditionally with the specified value and flags.
        """
        serialized = b"".join(pyuavcan.dsdl.serialize(value))
        self._db.execute(
            r"""
            insert or replace into registry (name, mutable, persistent, value) values (?, ?, ?, ?)
            """,
            (name, flags.mutable, flags.persistent, serialized),
        )
        self._db.commit()

    def delete(self, names: typing.Iterable[str]) -> None:
        """
        Removes specified registers from the storage.
        """
        self._db.executemany(r"delete from registry where name = ?", ((x,) for x in names))
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def _check_mutability(self) -> bool:
        try:
            self._db.execute("""create table if not exists `write_test` ( dummy int )""")
            self._db.execute("""drop table `write_test`""")
            self._db.commit()
        except sqlite3.OperationalError:
            return False
        return True


_logger = logging.getLogger(__name__)


def _unittest_storage_memory() -> None:
    from uavcan.primitive import String_1_0 as String, Unstructured_1_0 as Unstructured

    st = Storage()
    assert st.flags.mutable
    assert not st.flags.persistent
    assert not st.get_names()
    assert not st.get_name_by_index(0)
    assert None is st.get("foo")
    st.delete(["foo"])

    st.set("foo", Value(string=String("Hello world!")), flags=Flags(mutable=False, persistent=True))
    val_flags = st.get("foo")
    assert val_flags
    val, flags = val_flags
    assert isinstance(val, Value)
    assert val.string
    assert val.string.value.tobytes().decode() == "Hello world!"
    # Flags have been altered automatically to reflect the state of the storage backend -- here, it is volatile.
    assert not flags.mutable
    assert not st.flags.persistent

    # Override the same register.
    st.set("foo", Value(unstructured=Unstructured([1, 2, 3])), flags=Flags(mutable=True, persistent=False))
    val_flags = st.get("foo")
    assert val_flags
    val, flags = val_flags
    assert isinstance(val, Value)
    assert val.unstructured
    assert val.unstructured.value.tobytes() == b"\x01\x02\x03"
    assert flags.mutable
    assert not st.flags.persistent

    assert ["foo"] == st.get_names()
    assert "foo" == st.get_name_by_index(0)
    assert None is st.get_name_by_index(1)
    st.delete(["baz"])
    assert ["foo"] == st.get_names()
    st.delete(["foo", "baz"])
    assert [] == st.get_names()

    st.close()


def _unittest_storage_file() -> None:
    import os
    import tempfile
    from uavcan.primitive import Unstructured_1_0 as Unstructured

    # First, populate the database with registers.
    db_file = tempfile.mktemp(".db")
    print("DB file:", db_file)
    st = Storage(db_file)
    assert st.flags.mutable
    assert st.flags.persistent
    st.set("mutable", Value(unstructured=Unstructured([1, 2, 3])), flags=Flags(mutable=True, persistent=False))
    st.set("immutable", Value(unstructured=Unstructured([4, 5, 6])), flags=Flags(mutable=False, persistent=True))
    st.close()

    # Then re-open it in writeable mode and ensure correctness.
    st = Storage(db_file)
    val_flags = st.get("mutable")
    assert val_flags
    val, flags = val_flags
    assert isinstance(val, Value)
    assert val.unstructured
    assert val.unstructured.value.tobytes() == b"\x01\x02\x03"
    assert flags.mutable
    assert not flags.persistent

    val_flags = st.get("immutable")
    assert val_flags
    val, flags = val_flags
    assert isinstance(val, Value)
    assert val.unstructured
    assert val.unstructured.value.tobytes() == b"\x04\x05\x06"
    assert not flags.mutable
    assert flags.persistent
    st.close()

    # Then re-open it in read-only mode.
    os.chmod(db_file, 0o444)
    st = Storage(db_file)
    val_flags = st.get("mutable")
    assert val_flags
    _, flags = val_flags
    assert not flags.mutable
    assert not flags.persistent

    val_flags = st.get("immutable")
    assert val_flags
    _, flags = val_flags
    assert not flags.mutable
    assert flags.persistent
    st.close()
