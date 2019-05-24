import os
import random
import asyncio
import json
from quart import Quart, jsonify, render_template
from quart_cors import cors

dir_path = os.path.dirname(os.path.realpath(__file__))


def fileresponse(path):
    f = os.path.join(dir_path, path)
    if os.path.isfile(f + '.json'):
        with open(f + '.json', 'r') as file:
            return (file.read(), 200)

    return ('', 404)


class ServerSentEvent:
    def __init__(
            self,
            data: str,
            event: str
    ) -> None:
        self.data = data
        self.event = event

    def encode(self) -> bytes:
        message = f"data: {json.dumps(self.data)}"
        if self.event is not None:
            message = f"{message}\nevent: {self.event}"
        message = f"{message}\r\n\r\n"
        return message.encode('utf-8')


api_prefix = '/api/v1'

app = Quart(__name__)
app = cors(app)


@app.route(api_prefix + '/eventSource')
async def sse():
    async def send_events():
        data = [
            {
                "id": 0,
                "health": "CRITICAL"
            },
            {
                "id": 0,
                "health": 'WARNING'
            },
            {
                "id": 0,
                "health": 'OPERATIONAL'
            },
            {
                "id": 0,
                "health": 'ERROR'
            }
        ]

        while True:
            await asyncio.sleep(2)
            random.shuffle(data)
            event = ServerSentEvent(data=data[0], event='NODE_STATUS')
            yield event.encode()

    return send_events(), {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Transfer-Encoding': 'chunked',
    }


# Sink all undeclared routes so that vue can work with router properly
@app.route('/<path:path>')
def serve_mocks(path: str) -> str:
    x = fileresponse(path)
    return x

if __name__ == "__main__":
    app.run(port=5000)
