from quart import Quart, jsonify, render_template
from quart_cors import cors

app = Quart(__name__,
            static_folder='../frontend/dist/static',
            template_folder='../frontend/dist')
app = cors(app)

@app.route('/api/v1/nodes', methods=['GET'])
async def list_of_nodes():
    class NodeGetAllEntryResponse(object):
        def __init__(self, name, id, health, mode, uptime, vendorCode):
            self.name = name
            self.id = id
            self.health = health
            self.mode = mode
            self.uptime = uptime
            self.vendorCode = vendorCode

        def serialise(self):
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
async def catch_all(path):
    return await render_template('index.html')

app.run(port=5000)