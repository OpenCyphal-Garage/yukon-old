from quart import Blueprint, jsonify
from typing import Any, Dict

nodes_controller = Blueprint('nodes', __name__)


@nodes_controller.route('/', methods=['GET'])
async def list_of_nodes() -> Any:
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

    mock_responses = [
        NodeGetAllEntryResponse('node_0', 1, 'OK', 'OPERATIONAL', 200, 990),
        NodeGetAllEntryResponse('node_1', 2, 'WARNING', 'INITIALIZATION', 444, 30),
        NodeGetAllEntryResponse('xxx_5', 123, 'ERROR', 'MAINTAINANCE', 10000, 999),
        NodeGetAllEntryResponse('zzz_3', 6, 'CRITICAL', 'SOFTWARE_UPDATE', 5, 990),
        NodeGetAllEntryResponse('aa_4', 7, 'OK', 'OFFLINE', -1, 990)
    ]

    return jsonify([e.serialise() for e in mock_responses])


@nodes_controller.route('/<int:nodeId>/parameters', methods=['GET'])
async def node_details(nodeId) -> Any:
    class NodeParametersResponse(object):
        def __init__(self) -> None:
            pass

        def serialise(self) -> None:
            pass

    return jsonify('OK')


@nodes_controller.route('/<int:nodeId>/parameters/<string:param>', methods=['POST'])
async def node_details(nodeId, param) -> Any:
    return jsonify('Param set: ' + param)


@nodes_controller.route('/<int:nodeId>', methods=['GET'])
async def node_details(nodeId) -> Any:
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
                                            990, '4.3.2.1', '0xTOOMUCHBEEF', '1.2.3.4', 'my-awesome-uid', 'I am authentic')

    return jsonify(mock_response.serialise())
