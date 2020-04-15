#!/usr/bin/env python3
#
# Copyright (C) 2020  UAVCAN Development Team  <uavcan.org>
#               2020  dronesolutions.io. All rights reserved.
# This software is distributed under the terms of the MIT License.
#
"""
    Based on https://github.com/UAVCAN/pyuavcan/blob/master/tests/demo/basic_usage.py.
    Launches a demo UAVCAN node which serves the purpose of testing the Yukon backend
    functionaly.

.. automodule:: yavcan_node_demo
   :platform: Unix, Windows
   :synopsis: Runs the Yukon backend
   :members:

.. moduleauthor:: Nuno Marques <nuno.marques@dronesolutions.io>
"""

import os
import pathlib
import sys
import tempfile
from asyncio import Task, all_tasks, gather, get_event_loop, sleep

import pyuavcan
import pyuavcan.transport.udp

dsdl_generated_dir = pathlib.Path(
    tempfile.gettempdir(), 'dsdl', f'pyuavcan-v{pyuavcan.__version__}')
dsdl_generated_dir.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(dsdl_generated_dir))

# Generate the standard namespace.
print('\n\033[5mGenerating DSDL packages...\033[0m', file=sys.stderr)
print('These are being stored in:', dsdl_generated_dir, file=sys.stderr)
pyuavcan.dsdl.generate_package(
    root_namespace_directory=os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'public_regulated_data_types/uavcan'),
    output_directory=dsdl_generated_dir,
)

try:
    import pyuavcan.application
    import uavcan.node                      # noqa E402
    import uavcan.diagnostic                # noqa E402
except (ImportError, AttributeError):
    sys.stderr.write(
        '\n\n\033[91mFailed to import required DSDL packages. They might not have been generated correctly\n\033[0m')
    sys.exit(1)


class DemoApplication:
    """
        Starts a UAVCAN node which publishes data on a bus.
        By 04/15/2020, it only functions over UDP and publishes heartbeats and diagnostic msgs.
    """

    def __init__(self) -> None:
        transport = pyuavcan.transport.udp.UDPTransport('127.0.0.42/8')

        assert transport.local_node_id == 42

        node_info = uavcan.node.GetInfo_1_0.Response(
            protocol_version=uavcan.node.Version_1_0(
                *pyuavcan.UAVCAN_SPECIFICATION_VERSION),
            software_version=uavcan.node.Version_1_0(major=1, minor=0),
            name='org.uavcan.yukon.backend.monitor',
        )

        presentation = pyuavcan.presentation.Presentation(transport)
        self._node = pyuavcan.application.Node(presentation, node_info)
        self._node.heartbeat_publisher.mode = uavcan.node.Heartbeat_1_0.MODE_OPERATIONAL
        self._node.heartbeat_publisher.health = uavcan.node.Heartbeat_1_0.HEALTH_NOMINAL
        self._node.heartbeat_publisher.vendor_specific_status_code = \
            os.getpid() & (2 ** min(pyuavcan.dsdl.get_model(uavcan.node.Heartbeat_1_0)[
                'vendor_specific_status_code'].data_type.bit_length_set) - 1)

        self._pub_diagnostic_record = \
            self._node.presentation.make_publisher_with_fixed_subject_id(
                uavcan.diagnostic.Record_1_0)
        self._pub_diagnostic_record.priority = pyuavcan.transport.Priority.OPTIONAL
        self._pub_diagnostic_record.send_timeout = 2.0

        self._node.start()

    @property
    def node_started(self) -> bool:
        return self._node._started


async def main() -> int:
    """
        Main routine creates and starts the UAVCAN node and gathers and prints the
        running tasks of the main event loop.
    """
    app = DemoApplication()

    if app.node_started:
        sys.stdout.write('\n\033[92mDemo UAVCAN node started!\n\033[0m')

        app_tasks = all_tasks()

        async def list_tasks_periodically() -> None:
            """
                Print active tasks periodically for demo purposes.
            """
            import re

            def repr_task(t: Task) -> str:
                try:
                    out, = re.findall(r'^<([^<]+<[^>]+>)', str(t))
                except ValueError:
                    out = str(t)
                return out

            while True:
                print('\nActive tasks:\n' +
                      '\n'.join(map(repr_task, app_tasks)), file=sys.stderr)
                await sleep(10)

        get_event_loop().create_task(list_tasks_periodically())
        await gather(*app_tasks)
        return 0
    else:
        sys.stderr.write(
            '\n\n\033[91mFailed to start demo UAVCAN node!\n\033[0m')
        return 1

if __name__ == '__main__':
    try:
        get_event_loop().run_until_complete(main())
        get_event_loop().close()
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write('\n\n\033[94mDemo UAVCAN node terminated!\n\033[0m')
        sys.exit(0)
