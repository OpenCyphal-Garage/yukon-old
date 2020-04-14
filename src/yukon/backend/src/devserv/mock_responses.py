import os
import random
import asyncio
import json
from quart import Quart
from quart_cors import cors
from typing import Tuple
from typing import AsyncGenerator
from typing import Dict

dir_path = os.path.dirname(os.path.realpath(__file__))


def fileresponse(path: str) -> Tuple[str, int]:
    f = os.path.join(dir_path, path)
    if os.path.isfile(f + '.json'):
        with open(f + '.json', 'r') as file:
            return (file.read(), 200)
    else:
        return ('', 404)


class ServerSentEvent:
    """
    Sends a REST response to the client side. Example:

    .. code-block:: python

        from src.devserv.mock_responses import ServerSentEvent

        import asyncio
        import json
        import typing

        async def sse() -> typing.AsyncGenerator[bytes, None]:
            async def send_events() -> typing.AsyncGenerator[bytes, None]:
                data = [
                    {
                        "Test key": 0,
                        "Test value": "CRITICAL"
                    }
                ]

                while True:
                    await asyncio.sleep(2)
                    random.shuffle(data)
                    event = ServerSentEvent(data=json.dumps(data), event='NODE_STATUS')
                    yield event.encode()

            return send_events()

        loop = asyncio.get_event_loop()
        assert loop.run_until_complete(asyncio.gather(sse()))
    """
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

app = Quart(__name__,
            static_folder='../../../frontend/static/',
            template_folder='../../../frontend/')
app = cors(app)


@app.route(api_prefix + '/eventSource')
async def sse() -> Tuple[AsyncGenerator[bytes, None], Dict[str, str]]:
    async def send_events() -> AsyncGenerator[bytes, None]:
        data = [
            {
                "id": 0,
                "health": "CRITICAL"
            },
            {
                "id": 1,
                "health": 'WARNING'
            },
            {
                "id": 2,
                "health": 'OPERATIONAL'
            },
            {
                "id": 3,
                "health": 'ERROR'
            }
        ]

        while True:
            await asyncio.sleep(2)
            random.shuffle(data)
            event = ServerSentEvent(data=json.dumps(data), event='NODE_STATUS')
            yield event.encode()

    return send_events(), {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Transfer-Encoding': 'chunked',
    }


# Sink all undeclared routes so that vue can work with router properly
@app.route('/<path:path>')
def serve_mocks(path: str) -> Tuple[str, int]:
    return fileresponse(path)


if __name__ == "__main__":
    app.run(port=5000)
