# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import typing
import inspect
import logging
import pyuavcan


_logger = logging.getLogger(__name__)


def construct(expression: str) -> pyuavcan.transport.Transport:
    """
    The argument is a (Python) expression that yields a transport instance or a sequence thereof upon evaluation.
    In the latter case, the multiple transports will be joined under the same redundant transport instance,
    which may be heterogeneous (e.g., UDP+Serial).

    The node-ID for the local node is to be configured here as well, because per the UAVCAN architecture,
    this is a transport-layer property.

    To see supported transports and how they should be initialized, refer to https://pyuavcan.readthedocs.io.

    The transport expression does not need to explicitly reference the `pyuavcan.transport` module
    because its contents are wildcard-imported for convenience.
    Further, when specifying a transport class, the suffix `Transport` may be omitted;
    e.g., `UDPTransport` and `UDP` are equivalent.
    Examples showcasing loopback, CAN, and heterogeneous UDP+Serial::

        Loopback(None)
        CAN(can.media.socketcan.SocketCANMedia('vcan0',64),42)
        UDP('127.42.0.123',anonymous=True),Serial("/dev/ttyUSB0",None)
    """
    context = _make_evaluation_context()
    out = eval(expression, context)
    _logger.debug("Expression %r yields %r", expression, out)
    if not isinstance(out, pyuavcan.transport.Transport):
        raise ValueError(
            f"The expression {expression!r} yields an instance of {type(out).__name__!r}. "
            f"Expected an instance of pyuavcan.transport.Transport."
        )
    return out


def _make_evaluation_context() -> typing.Dict[str, typing.Any]:
    def handle_import_error(parent_module_name: str, ex: ImportError) -> None:
        try:
            tr = parent_module_name.split(".")[2]
        except LookupError:
            tr = parent_module_name
        _logger.info("Transport %r is not available due to the missing dependency %r", tr, ex.name)

    # noinspection PyTypeChecker
    pyuavcan.util.import_submodules(pyuavcan.transport, error_handler=handle_import_error)

    context: typing.Dict[str, typing.Any] = {
        "pyuavcan": pyuavcan,
    }

    # Expose pre-imported transport modules for convenience.
    for name, module in inspect.getmembers(pyuavcan.transport, inspect.ismodule):
        if not name.startswith("_"):
            context[name] = module

    # Pre-import transport classes for convenience.
    transport_base = pyuavcan.transport.Transport
    # Suppressing MyPy false positive: https://github.com/python/mypy/issues/5374
    for cls in pyuavcan.util.iter_descendants(transport_base):  # type: ignore
        if not cls.__name__.startswith("_") and cls is not transport_base:
            name = cls.__name__.rpartition(transport_base.__name__)[0]
            assert name
            context[name] = cls

    _logger.debug("Transport expression evaluation context (on the next line):\n%r", context)
    return context
