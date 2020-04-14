#!/usr/bin/env python3
import asyncio
import pathlib
import tempfile

import os
import sys
import pyuavcan
import pyuavcan.transport.udp

dsdl_generated_dir = pathlib.Path(tempfile.gettempdir(), 'dsdl', f'pyuavcan-v{pyuavcan.__version__}')
dsdl_generated_dir.mkdir(parents=True, exist_ok=True)
print('Generated DSDL packages will be stored in:', dsdl_generated_dir, file=sys.stderr)

sys.path.insert(0, str(dsdl_generated_dir))

# Generate the standard namespace.
pyuavcan.dsdl.generate_package(
    root_namespace_directory=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'public_regulated_data_types/uavcan'),
    output_directory=dsdl_generated_dir,
)

import pyuavcan.application
import uavcan.node                      # noqa E402
import uavcan.diagnostic                # noqa E402


class DemoApplication:
    def __init__(self):
        transport = pyuavcan.transport.udp.UDPTransport('127.0.0.42/8')

        assert transport.local_node_id == 42

        node_info = uavcan.node.GetInfo_1_0.Response(
            protocol_version=uavcan.node.Version_1_0(*pyuavcan.UAVCAN_SPECIFICATION_VERSION),
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
            self._node.presentation.make_publisher_with_fixed_subject_id(uavcan.diagnostic.Record_1_0)
        self._pub_diagnostic_record.priority = pyuavcan.transport.Priority.OPTIONAL
        self._pub_diagnostic_record.send_timeout = 2.0

        self._node.start()


if __name__ == '__main__':
    app = DemoApplication()
    app_tasks = asyncio.Task.all_tasks()

    async def list_tasks_periodically() -> None:
        """Print active tasks periodically for demo purposes."""
        import re

        def repr_task(t: asyncio.Task) -> str:
            try:
                out, = re.findall(r'^<([^<]+<[^>]+>)', str(t))
            except ValueError:
                out = str(t)
            return out

        while True:
            print('\nActive tasks:\n' + '\n'.join(map(repr_task, asyncio.Task.all_tasks())), file=sys.stderr)
            await asyncio.sleep(10)

    asyncio.get_event_loop().create_task(list_tasks_periodically())
    asyncio.get_event_loop().run_until_complete(asyncio.gather(*app_tasks))
