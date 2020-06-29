import os
import sys
import random
import argparse
import asyncio
import nest_asyncio
import json
from quart import Quart
from quart_cors import cors
from typing import Tuple
from typing import AsyncGenerator
from typing import Dict

dir_path = os.path.dirname(os.path.realpath(__file__))
api_prefix = '/api/v1'


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


class MockLoader:
    def __init__(self, sys_descr, sess_descr) -> None:
        self._sys_descr = sys_descr
        self._sess_descr = sess_descr

        self._app = Quart(__name__,
                          static_folder='../../../frontend/static/',
                          template_folder='../../../frontend/')
        self._app = cors(self._app)

        self.load_mock_system_description()

        @self.app.route(api_prefix + '/eventSource')
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
                    event = ServerSentEvent(
                        data=json.dumps(data), event='NODE_STATUS')
                    yield event.encode()

            return send_events(), {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Transfer-Encoding': 'chunked',
            }

    def load_mock_system_description(self) -> Tuple[str, int]:
        with open(os.path.join(dir_path, self.sys_descr + ".json")) as json_file:
            data = json.load(json_file)

            if 'bus' in data:
                @self.app.route(os.path.join(api_prefix, 'bus'))
                async def bus_mock() -> Tuple[str, int]:
                    return self.mock_response(self.sys_descr, data['bus'])

            if 'nodes' in data:
                if data['nodes']['detail']:
                    @self.app.route(os.path.join(api_prefix, 'nodes'))
                    async def nodes_mock() -> Tuple[str, int]:
                        return self.mock_response(self.sys_descr, data['nodes']['detail'])

                    # TODO: add way of dynamically loading a router per node
                    for nodes in data['nodes']['detail']:
                        if nodes['id'] == 0:
                            @self.app.route(os.path.join(api_prefix, 'nodes/0/registers'))
                            async def nodes_id0_mock() -> Tuple[str, int]:
                                return self.mock_response(self.sys_descr, data['nodes']['detail'][0]['registers'])

                if data['nodes']['plugandplay']:
                    @self.app.route(os.path.join(api_prefix, 'nodes/plugandplay'))
                    async def plugandplay_mock() -> Tuple[str, int]:
                        return self.mock_response(self.sys_descr, data['nodes']['plugandplay'])

                if data['nodes']['grv']:
                    @self.app.route(os.path.join(api_prefix, 'nodes/grv'))
                    async def global_register_view_mock() -> Tuple[str, int]:
                        return self.mock_response(self.sys_descr, data['nodes']['grv'])

            if 'health' in data:
                @self.app.route(os.path.join(api_prefix, 'health'))
                async def health_mock() -> Tuple[str, int]:
                    return self.mock_response(self.sys_descr, data['health'])

            if 'types' in data:
                @self.app.route(os.path.join(api_prefix, 'types'))
                async def types_mock() -> Tuple[str, int]:
                    return self.mock_response(self.sys_descr, data['types'])

    def load_mock_session_description(self) -> Tuple[str, int]:
        # TODO requires a log loader
        return ('', 404)

    @property
    def app(self) -> Quart:
        return self._app

    @property
    def sys_descr(self):
        return self._sys_descr

    @property
    def sess_descr(self):
        return self._sess_descr

    def mock_response(self, path: str, elem) -> Tuple[str, int]:
        response = json.dumps(elem)
        if response:
            return (json.dumps(elem), 200)
        else:
            return ('', 404)


if __name__ == "__main__":
    sys.stdout.write('\n\033[92mMock Backend process started!\n\033[0m')

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--system-description", dest='sysdesc_file', type=str,
                        help="Mock System description relative file path, defaults to description_example/sys_description",
                        default="description/example/example_sys_description")
    parser.add_argument("-t", "--session-description", dest='sessdesc_file', type=str,
                        help="Mock Session description relative file path, defaults to description_example/sess_description",
                        default="description/example/example_sess_description")

    # Parse arguments
    args = parser.parse_args()

    mock_backend = MockLoader(args.sysdesc_file, args.sessdesc_file)

    try:
        mock_backend.app.run(port=5000)
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write('\n\n\033[94mMock process terminated!\n\033[0m')
        sys.exit(0)
