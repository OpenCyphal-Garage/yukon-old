#!/usr/bin/env python3
#
# Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
#
# Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
#

from quart import Quart, jsonify, render_template
from quart_cors import cors
from typing import Any, Dict

app = Quart(__name__,
            static_folder='../../frontend/dist/static',
            template_folder='../../frontend/dist')
app = cors(app)


@app.route('/api/v1/nodes', methods=['GET'])
async def list_of_nodes() -> Any:
    class NodeGetAllEntryResponse(object):
        def __init__(self, name: str, id: int, health: str, mode: str, uptime: int, vendorCode: str) -> None:
            self.name = name
            self.id = id
            self.health = health
            self.mode = mode
            self.uptime = uptime
            self.vendorCode = vendorCode

        def serialise(self) -> Dict[str, Any]:
            return {
                'name': self.name,
                'id': self.id,
                'health': self.health,
                'mode': self.mode,
                'uptime': self.uptime,
                'vendorCode': self.vendorCode
            }

    mockResponses = [
        NodeGetAllEntryResponse('node_0', 1, 'OK', 'OPERATIONAL', 200, '990'),
        NodeGetAllEntryResponse('node_1', 2, 'WARNING', 'INITIALISATION', 444, '30'),
        NodeGetAllEntryResponse('xxx_5', 123, 'ERROR', 'MAINTAINANCE', 10000, '999'),
        NodeGetAllEntryResponse('zzz_3', 6, 'CRITICAL', 'SOFTWARE_UPDATE', 5, '990'),
        NodeGetAllEntryResponse('aa_4', 7, 'OK', 'OFFLINE', -1, '990')
    ]

    return jsonify([e.serialise() for e in mockResponses])


# Sink all undeclared routes so that vue can work with router properly
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def catch_all(path: str) -> str:
    return await render_template('index.html')

app.run(port=5000)
