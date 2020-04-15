#!/usr/bin/env python3
#
# Copyright (C) 2019  UAVCAN Development Team  <uavcan.org>
#               2020  dronesolutions.io. All rights reserved.
# This software is distributed under the terms of the MIT License.
#

"""
.. automodule:: nodes
   :platform: Unix, Windows
   :synopsis: Runs the Yukon backend
   :members:

.. moduleauthor:: Theodoros Ntakouris <zarkopafilis@gmail.com>
.. moduleauthor:: Nuno Marques <nuno.marques@dronesolutions.io>
"""

import asyncio
import pathlib
import sys
import tempfile
from typing import Any, Awaitable, Optional, Tuple

import pyuavcan
import pyuavcan.transport.udp
from quart import Blueprint, Response, jsonify, request

dsdl_generated_dir = pathlib.Path(
    tempfile.gettempdir(), 'dsdl', f'pyuavcan-v{pyuavcan.__version__}')
dsdl_generated_dir.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(dsdl_generated_dir))

try:
    import pyuavcan.application             # noqa E402
    import uavcan.node                      # noqa E402
    import uavcan.node.Version_1_0          # noqa E402
    import uavcan.node.Heartbeat_1_0        # noqa E402
except (ImportError, AttributeError):
    sys.stderr.write(
        '\n\n\033[91mFailed to import required DSDL packages. They might not have been generated correctly\n\033[0m')
    sys.exit(1)


class Controller:
    """
        Provides utillities to bus and node monitoring and the required applicational routing
        to the endpoints.
    """

    def __init__(self, node_list: list = list(), nodeid_list: list = list()) -> None:
        # Blueprint backend application properties init
        self._nodes_controller = Blueprint('nodes', __name__)

        # Array of online nodes and its IDs
        self._node_list = node_list
        self._nodeid_list = nodeid_list

        # Map for node health
        self._node_health_code = {uavcan.node.Heartbeat_1_0.HEALTH_NOMINAL: 'NOMINAL',
                                  uavcan.node.Heartbeat_1_0.HEALTH_ADVISORY: 'ADVISORY',
                                  uavcan.node.Heartbeat_1_0.HEALTH_CAUTION: 'CAUTION',
                                  uavcan.node.Heartbeat_1_0.HEALTH_WARNING: 'WARNING'}

        # Map for node mode
        self._node_mode_code = {uavcan.node.Heartbeat_1_0.MODE_OPERATIONAL: 'OPERATIONAL',
                                uavcan.node.Heartbeat_1_0.MODE_INITIALIZATION: 'INITIALIZATION',
                                uavcan.node.Heartbeat_1_0.MODE_MAINTENANCE: 'MAINTENANCE',
                                uavcan.node.Heartbeat_1_0.MODE_SOFTWARE_UPDATE: 'SOFTWARE_UPDATE',
                                uavcan.node.Heartbeat_1_0.MODE_OFFLINE: 'OFFLINE'}

        ######################
        # ENDPOINT RESPONSES #
        ######################
        @self.nodes_controller.route('/', methods=['GET'])
        async def list_of_nodes() -> Response:
            """
                Reponse to the home page, providing data for the existing nodes in a specific bus.
            """
            return jsonify([e.__dict__ for e in self.get_node_list_ref()])

        @self.nodes_controller.route('/<int:nodeId>/parameters', methods=['GET'])
        async def node_parameter_list(nodeId: int) -> Response:
            # For now, send a mock reponses as an example
            mock_responses = [
                NodeParameters('gnss.uart_on', 'boolean',
                               True, False, None, None),
                NodeParameters('gnss.somemetric', 'real', 0.445, 1.0, 0.0, 10.0)]

            return jsonify([e.__dict__ for e in mock_responses])

        @self.nodes_controller.route('/<int:nodeId>/parameters/<string:param>', methods=['PUT'])
        async def node_parameter_update(nodeId: int, param: str) -> Tuple[Response, int]:
            body = await request.get_json()
            return body['value'], 200

        @self.nodes_controller.route('/<int:nodeId>', methods=['GET'])
        async def node_details(nodeId: int) -> Response:
            # For now, send a mock reponses as an example
            mock_responses = [NodeDetails('node_0', nodeId, 'OK', 'OPERATIONAL', 200,
                                          990, '4.3.2.1', '0xTOOMUCHBEEF', '1.2.3.4', 'my-awesome-uid',
                                          'I am authentic')]

            return jsonify([e.__dict__ for e in mock_responses])

        @self.nodes_controller.route('/<int:nodeId>/shutdown', methods=['PUT'])
        async def node_shutdown(nodeId: int) -> Tuple[Response, int]:
            return "", 200

        @self.nodes_controller.route('/<int:nodeId>/firmwareupdate', methods=['PUT'])
        async def node_firmware_update(nodeId: int, param: str) -> Tuple[Response, int]:
            body = await request.get_json()
            return body['name'], 200

    @property
    def nodes_controller(self) -> Blueprint:
        return self._nodes_controller

    def get_node_list_ref(self) -> list:
        return self._node_list

    def get_nodeid_list_ref(self) -> list:
        return self._nodeid_list

    def health_to_text(self, health_code: int) -> Optional[str]:
        return self._node_health_code.get(health_code)

    def mode_to_text(self, mode_code: int) -> Optional[str]:
        return self._node_mode_code.get(mode_code)


class NodeInfo:
    """
        Class strucuture for UAVCAN node info.
    """

    def __init__(self, name: str, id: int, health: Optional[str], mode: Optional[str], uptime: int,
                 vendor_code: int) -> None:
        self.__dict__ = {
            'name': name,
            'id': id,
            'health': health,
            'mode': mode,
            'uptime': uptime,
            'vendorCode': vendor_code
        }


class NodeParameters:
    """
        Class structure for UAVCAN node params.
    """

    def __init__(self, name: str, type_: str, value: Any, default: Any, min: Any = None, max: Any = None) -> None:
        self.__dict__ = {
            'name': name,
            'type': type_.lower(),
            'value': value.lower() if value is str else value,
            'default': default,
            'min': min,
            'max': max
        }


class NodeDetails:
    """
        Class structure for UAVCAN node overall details response to 430 GetInfo.1.0.uavcan
    """

    def __init__(self, name: str, id: int, health: str, mode: str,
                 uptime: int, vendor_code: int, software_version: str,
                 crc: str, hardware_version: str, uid: str, authenticity: str) -> None:
        self.__dict_ = {
            'name': name,
            'id': id,
            'health': health,
            'mode': mode,
            'uptime': uptime,
            'vendorCode': vendor_code,
            'softwareVersion': software_version,
            'crc': crc,
            'hardware_version': hardware_version,
            'uid': uid,
            'authenticity': authenticity
        }


class Monitor(Controller):
    """
        UAVCAN node created in a specific bus, which purpose is to gather data from other existing
        nodes and retrieve data from the bus itself, the nodes and the packets being exchanged.
    """

    def __init__(self) -> None:
        super().__init__()

        # As by 15/04/2020, this only supports UDP and a static node ID on the loopback interface
        transport = pyuavcan.transport.udp.UDPTransport('127.0.0.43/8')

        assert transport.local_node_id == 43

        node_info = uavcan.node.GetInfo_1_0.Response(
            protocol_version=uavcan.node.Version_1_0(
                *pyuavcan.UAVCAN_SPECIFICATION_VERSION),
            software_version=uavcan.node.Version_1_0(major=1, minor=0),
            name='org.uavcan.yukon.backend.monitor',
        )

        presentation = pyuavcan.presentation.Presentation(transport)
        self._node = pyuavcan.application.Node(presentation, node_info)

        # As by 15/04/2020, this only supports passive node info gathering through the Hearbeat msgs content
        self._sub_heartbeat = self._node.presentation.make_subscriber(
            uavcan.node.Heartbeat_1_0, 32085)

        self._sub_heartbeat.receive_in_background(self._handle_heartbeat)
        self._monitor_task = self._monitor_run()

    async def _monitor_run(self) -> Awaitable:
        self._node.start()
        return await asyncio.gather(*asyncio.Task.all_tasks())

    async def _handle_heartbeat(self, msg: uavcan.node.Heartbeat_1_0,
                                metadata: pyuavcan.transport.TransferFrom) -> None:
        node_info = NodeInfo("node", metadata.source_node_id, super().health_to_text(msg.health),
                             super().mode_to_text(msg.mode), msg.uptime, msg.vendor_specific_status_code)
        if metadata.source_node_id not in super().get_nodeid_list_ref():
            super().get_nodeid_list_ref().append(node_info.__dict__['id'])
            super().get_node_list_ref().append(node_info)
        else:
            super().get_node_list_ref()[super().get_nodeid_list_ref().index(
                node_info.__dict__['id'])] = node_info

    @property
    def monitor_started(self) -> bool:
        return self._node._started
