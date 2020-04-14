from quart import Blueprint, jsonify, request, Response
from typing import Any, Dict, Tuple

nodes_controller = Blueprint('nodes', __name__)

import asyncio
import pathlib
import tempfile

import os
import sys
import pyuavcan
import pyuavcan.transport.udp

dsdl_generated_dir = pathlib.Path(tempfile.gettempdir(), 'dsdl', f'pyuavcan-v{pyuavcan.__version__}')
dsdl_generated_dir.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(dsdl_generated_dir))

import pyuavcan.application
import uavcan.node                      # noqa E402
import uavcan.diagnostic                # noqa E402

heartbeat = 0


# Create the monitor node
class MonitorNode:
    def __init__(self):
        transport = pyuavcan.transport.udp.UDPTransport('127.0.0.43/8')

        assert transport.local_node_id == 43

        node_info = uavcan.node.GetInfo_1_0.Response(
            protocol_version=uavcan.node.Version_1_0(*pyuavcan.UAVCAN_SPECIFICATION_VERSION),
            software_version=uavcan.node.Version_1_0(major=1, minor=0),
            name='org.uavcan.yukon.backend.monitor',
        )

        presentation = pyuavcan.presentation.Presentation(transport)
        self._node = pyuavcan.application.Node(presentation, node_info)
        self._sub_heartbeat = self._node.presentation.make_subscriber(uavcan.node.Heartbeat_1_0, 42)
        self._sub_heartbeat.receive_in_background(self._handle_heartbeat)

        self._node.start()

    async def _handle_heartbeat(self, msg: uavcan.node.Heartbeat_1_0, metadata: pyuavcan.transport.TransferFrom) -> None:
        global heartbeat
        heartbeat = metadata.source_node_id
        print('Got heartbeat')

monitor_node = MonitorNode()


@nodes_controller.route('/', methods=['GET'])
async def list_of_nodes() -> Tuple[Response, None]:
    class NodeGetAllEntryResponse(object):
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

    global heartbeat
    print(heartbeat)
    mock_responses = [
        NodeGetAllEntryResponse('node_0', 1, 'OK', 'OPERATIONAL', 200, 990),
        NodeGetAllEntryResponse('node_1', 2, 'WARNING', 'INITIALIZATION', 444, 30),
        NodeGetAllEntryResponse('xxx_5', 123, 'ERROR', 'MAINTAINANCE', 10000, 999),
        NodeGetAllEntryResponse('zzz_3', 6, 'CRITICAL', 'SOFTWARE_UPDATE', 5, 990),
        NodeGetAllEntryResponse('aa_4', 7, 'OK', 'OFFLINE', -1, 990)
    ]

    return jsonify([e.serialise() for e in mock_responses])


@nodes_controller.route('/<int:nodeId>/parameters', methods=['GET'])
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

    mock_responses = [
        NodeParametersResponse('gnss.uart_on', 'boolean', True, False, None, None),
        NodeParametersResponse('gnss.somemetric', 'real', 0.445, 1.0, 0.0, 10.0)]

    return jsonify([e.serialise() for e in mock_responses])


@nodes_controller.route('/<int:nodeId>/parameters/<string:param>', methods=['PUT'])
async def node_parameter_update(nodeId, param) -> Tuple[Response, int]:
    body = await request.get_json()
    return body['value'], 200


@nodes_controller.route('/<int:nodeId>', methods=['GET'])
async def node_details(nodeId) -> Tuple[Response, None]:
    class NodeGetDetailsResponse(object):
        def __init__(self, name: str, id: int, health: str, mode: str, uptime: int, vendor_code: int,
                     software_version: str, crc: str, hardware_version: str, uid: str, authenticity: str) -> None:
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

    mock_responses = NodeGetDetailsResponse('node_0', nodeId, 'OK', 'OPERATIONAL', 200,
                                            990, '4.3.2.1', '0xTOOMUCHBEEF', '1.2.3.4', 'my-awesome-uid',
                                            'I am authentic')

    return jsonify(mock_responses.serialise())


@nodes_controller.route('/<int:nodeId>/shutdown', methods=['PUT'])
async def node_shutdown(nodeId) -> Tuple[Response, int]:
    return "", 200


@nodes_controller.route('/<int:nodeId>/firmwareupdate', methods=['PUT'])
async def node_firmware_update(nodeId, param) -> Tuple[Response, int]:
    body = await request.get_json()
    return body['name'], 200
