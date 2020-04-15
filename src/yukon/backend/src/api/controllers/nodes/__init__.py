#!/usr/bin/env python3
#
# Copyright (C) 2019  UAVCAN Development Team  <uavcan.org>
#               2020  dronesolutions.io. All rights reserved.
# This software is distributed under the terms of the MIT License.
#

"""
.. module:: controllers.nodes
   :platform: Unix, Windows
   :synopsis: Runs the Yukon backend

.. moduleauthor:: Theodoros Ntakouris <zarkopafilis@gmail.com>
.. moduleauthor:: Nuno Marques <nuno.marques@dronesolutions.io>
"""

import pyuavcan.transport.udp
import pyuavcan
import sys
import os
import tempfile
import pathlib
import asyncio
from quart import Blueprint, jsonify, request, Response
from typing import Any, Dict, Tuple

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


class Controller():
    """
        Provides utillities to bus and node monitoring and the required applicational routing
        to the endpoints.
    """

    def __init__(self, node_list=list(), nodeid_list=list()):
        # Blueprint backend application properties init
        self._nodes_controller = Blueprint('nodes', __name__)

        # Array of online nodes and its IDs
        self._node_list = node_list
        self._nodeid_list = nodeid_list

        ######################
        # ENDPOINT RESPONSES #
        ######################
        @self.nodes_controller.route('/', methods=['GET'])
        async def list_of_nodes() -> Tuple[Response, None]:
            """
                Reponse to the home page, providing data for the existing nodes in a specific bus.
            """
            return jsonify([e.serialise() for e in self.node_list])

        @self.nodes_controller.route('/<int:nodeId>/parameters', methods=['GET'])
        async def node_parameter_list(nodeId) -> Tuple[Response, None]:
            class NodeParametersResponse(object):
                def __init__(self, name: str, type_: str, value: Any, default: Any, min: Any = None, max: Any = None) -> None:
                    self.name = name
                    self.type = type_
                    self.value = value
                    self.default = default
                    self.min = min
                    self.max = max

                def serialise(self) -> Dict[str, Any]:
                    ret = {
                        'name': self.name,
                        'type': self.type.lower(),
                        'value': self.value,
                        'default': self.default,
                    }

                    if (self.value is str):
                        ret['value'] = self.value.lower()

                    if (self.min is not None):
                        ret['min'] = self.min

                    if (self.max is not None):
                        ret['max'] = self.max

                    return ret

            # For now, send a mock reponses as an example
            mock_responses = [
                NodeParametersResponse('gnss.uart_on', 'boolean',
                                       True, False, None, None),
                NodeParametersResponse('gnss.somemetric', 'real', 0.445, 1.0, 0.0, 10.0)]

            return jsonify([e.serialise() for e in mock_responses])

        @self.nodes_controller.route('/<int:nodeId>/parameters/<string:param>', methods=['PUT'])
        async def node_parameter_update(nodeId, param) -> Tuple[Response, int]:
            body = await request.get_json()
            return body['value'], 200

        @self.nodes_controller.route('/<int:nodeId>', methods=['GET'])
        async def node_details(nodeId) -> Tuple[Response, None]:
            class NodeGetDetailsResponse(object):
                def __init__(self, name: str, id: int, health: str, mode: str,
                             uptime: int, vendor_code: int, software_version: str,
                             crc: str, hardware_version: str, uid: str, authenticity: str) -> None:
                    self.name = name
                    self.id = id
                    self.health = health
                    self.mode = mode
                    self.uptime = uptime
                    self.vendor_code = vendor_code
                    self.software_version = software_version
                    self.crc = crc
                    self.hardware_version = hardware_version
                    self.uid = uid
                    self.authenticity = authenticity

                def serialise(self) -> Dict[str, Any]:
                    return {
                        'name': self.name,
                        'id': self.id,
                        'health': self.health,
                        'mode': self.mode,
                        'uptime': self.uptime,
                        'vendorCode': self.vendor_code,
                        'softwareVersion': self.software_version,
                        'crc': self.crc,
                        'hardware_version': self.hardware_version,
                        'uid': self.uid,
                        'authenticity': self.authenticity
                    }

            # For now, send a mock reponses as an example
            mock_responses = NodeGetDetailsResponse('node_0', nodeId, 'OK', 'OPERATIONAL', 200,
                                                    990, '4.3.2.1', '0xTOOMUCHBEEF', '1.2.3.4', 'my-awesome-uid',
                                                    'I am authentic')

            return jsonify(mock_responses.serialise())

        @self.nodes_controller.route('/<int:nodeId>/shutdown', methods=['PUT'])
        async def node_shutdown(nodeId) -> Tuple[Response, int]:
            return "", 200

        @self.nodes_controller.route('/<int:nodeId>/firmwareupdate', methods=['PUT'])
        async def node_firmware_update(nodeId, param) -> Tuple[Response, int]:
            body = await request.get_json()
            return body['name'], 200

    @property
    def nodes_controller(self):
        return self._nodes_controller

    @property
    def node_list(self):
        return self._node_list

    @property
    def nodeid_list(self):
        return self._nodeid_list

    @classmethod
    def health_to_text(self, health_code):
        node_health_code = {uavcan.node.Heartbeat_1_0.HEALTH_NOMINAL: 'NOMINAL',
                            uavcan.node.Heartbeat_1_0.HEALTH_ADVISORY: 'ADVISORY',
                            uavcan.node.Heartbeat_1_0.HEALTH_CAUTION: 'CAUTION',
                            uavcan.node.Heartbeat_1_0.HEALTH_WARNING: 'WARNING'}
        return node_health_code.get(health_code)

    @classmethod
    def mode_to_text(self, mode_code):
        node_mode_code = {uavcan.node.Heartbeat_1_0.MODE_OPERATIONAL: 'OPERATIONAL',
                          uavcan.node.Heartbeat_1_0.MODE_INITIALIZATION: 'INITIALIZATION',
                          uavcan.node.Heartbeat_1_0.MODE_MAINTENANCE: 'MAINTENANCE',
                          uavcan.node.Heartbeat_1_0.MODE_SOFTWARE_UPDATE: 'SOFTWARE_UPDATE',
                          uavcan.node.Heartbeat_1_0.MODE_OFFLINE: 'OFFLINE'}
        return node_mode_code.get(mode_code)


class NodeInfo(object):
    """
        Class strucuture for UAVCAN node info.
    """

    def __init__(self, name: str, id: int, health: str, mode: str, uptime: int, vendor_code: int) -> None:
        self.name = name
        self.id = id
        self.health = health
        self.mode = mode
        self.uptime = uptime
        self.vendor_code = vendor_code

    def serialise(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'id': self.id,
            'health': self.health,
            'mode': self.mode,
            'uptime': self.uptime,
            'vendorCode': self.vendor_code
        }


class Monitor(Controller):
    """
        UAVCAN node created in a specific bus, which purpose is to gather data from other existing
        nodes and retrieve data from the bus itself, the nodes and the packets being exchanged.
    """

    def __init__(self):
        Controller.__init__(self)
        asyncio.get_event_loop().create_task(self._monitor_run())

    async def _monitor_run(self) -> int:
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

        self._node.start()
        await asyncio.gather(*asyncio.all_tasks())

    async def _handle_heartbeat(self, msg: uavcan.node.Heartbeat_1_0, metadata: pyuavcan.transport.TransferFrom) -> None:
        if metadata.source_node_id not in self.nodeid_list:
            node_info = NodeInfo("node", metadata.source_node_id, self.health_to_text(msg.health),
                                 self.mode_to_text(msg.mode), msg.uptime, msg.vendor_specific_status_code)

            self.nodeid_list.append(node_info.id)
            self.node_list.append(node_info)

    @property
    def monitor_started(self):
        return self._node._started
