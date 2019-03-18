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
