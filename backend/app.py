from quart import Quart, jsonify, render_template
from quart_cors import cors
import requests

app = Quart(__name__,
            static_folder='../frontend/dist/static',
            template_folder='../frontend/dist')
app = cors(app)

@app.route('/api/v1/nodes', methods=['GET'])
async def list_of_nodes():
    class NodeGetAllEntryResponse(object):
        def __init__(self, name, id, status, uptime, vendorCode):
            self.name = name
            self.id = id
            self.status = status
            self.uptime = uptime
            self.vendorCode = vendorCode

        def serialise(self):
            return {
                'name': self.name,
                'id': self.id,
                'status': self.status,
                'uptime': self.uptime,
                'vendorCode': self.vendorCode
            }

    mockResponses = [
        NodeGetAllEntryResponse('node_0', 1, 'UP', 200, '990'),
        NodeGetAllEntryResponse('node_1', 2, 'UP', 444, '30'),
        NodeGetAllEntryResponse('xxx_5', 123, 'UP', 10000, '999')
    ]

    return jsonify([e.serialise() for e in mockResponses])

# Sink all undeclared routes so that vue can work with router properly
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def catch_all(path):
    return await render_template('index.html')

app.run(port=5000)