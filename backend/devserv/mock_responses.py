import os
from quart import Quart, jsonify, render_template
from quart_cors import cors

dir_path = os.path.dirname(os.path.realpath(__file__))


def fileresponse(path):
    f = os.path.join(dir_path, path)
    if os.path.isfile(f + '.json'):
        with open(f + '.json', 'r') as file:
            return (file.read(), 200)

    return ('', 404)

api_prefix = '/api/v1'

app = Quart(__name__)
app = cors(app)


# Sink all undeclared routes so that vue can work with router properly
@app.route('/<path:path>')
def serve_mocks(path: str) -> str:
    x = fileresponse(path)
    return x

if __name__ == "__main__":
    app.run(port=5000)
