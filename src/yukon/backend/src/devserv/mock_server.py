import os
import sys
import random
import argparse
import asyncio
import nest_asyncio
import json
from quart import Quart, Response
from quart_cors import cors
from typing import Tuple
from typing import AsyncGenerator
from typing import Dict

dir_path = os.path.dirname(os.path.realpath(__file__))
api_prefix = '/api/v1'

def rename(newname):
    def decorator(f):
        f.__name__ = newname
        return f
    return decorator


class ServerSentEvent:
    """
    Server Sent Events (SSE) response to the client side. Allows the server to
    "push" information to the client. Example:

    .. code-block:: python

        from devserv.mock_responses import ServerSentEvent

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

        @self.app.route(api_prefix + '/eventSource')
        async def sse() -> Tuple[AsyncGenerator[bytes, None], Dict[str, str]]:
            async def send_events() -> AsyncGenerator[bytes, None]:
                data = [
                    {
                        "id": 0,
                        "health": "WARNING"
                    },
                    {
                        "id": 1,
                        "health": 'WARNING'
                    },
                    {
                        "id": 2,
                        "health": 'WARNING'
                    },
                    {
                        "id": 3,
                        "health": 'WARNING'
                    }
                ]

                while True:
                    await asyncio.sleep(1)
                    random.shuffle(data)
                    event = ServerSentEvent(
                        data=data[0], event='NODE_STATUS')
                    yield event.encode()

            return Response(send_events(), mimetype="text/event-stream")

        self.load_mock_system_description()
        self.load_mock_session_description()


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

                    for nodes in data['nodes']['detail']:
                        @self.app.route(os.path.join(api_prefix, 'nodes/' + str(nodes['id'])))
                        @rename('nodes_id' + str(nodes['id']) + '_mock()')
                        async def f() -> Tuple[str, int]:
                            return self.mock_response(self.sys_descr, data['nodes']['detail'][nodes['id']])

                        if 'registers' in nodes:
                            @self.app.route(os.path.join(api_prefix, 'nodes/' + str(nodes['id']) + '/registers'))
                            @rename('nodes_id' + str(nodes['id']) + '_registers_mock()')
                            async def f() -> Tuple[str, int]:
                                return self.mock_response(self.sys_descr, data['nodes']['detail'][nodes['id']]['registers'])

                        if 'publishers' in nodes:
                            @self.app.route(os.path.join(api_prefix, 'nodes/' + str(nodes['id']) + '/publishers'))
                            @rename('nodes_id' + str(nodes['id']) + '_pub_mock()')
                            async def f() -> Tuple[str, int]:
                                return self.mock_response(self.sys_descr, data['nodes']['detail'][nodes['id']]['publishers'])

                        if 'subscribers' in nodes:
                            @self.app.route(os.path.join(api_prefix, 'nodes/' + str(nodes['id']) + '/subscribers'))
                            @rename('nodes_id' + str(nodes['id']) + '_sub_mock()')
                            async def f() -> Tuple[str, int]:
                                return self.mock_response(self.sys_descr, data['nodes']['detail'][nodes['id']]['subscribers'])

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
        with open(os.path.join(dir_path, self.sess_descr + ".json")) as json_file:
            data = json.load(json_file)

            if 'interactions' in data:
                for interaction in data['interactions']:
                    if interaction['nodes']:
                        for node in interaction['nodes']:
                            if 'publishers' in node:
                                break
                                # Adds temporary interaction change
                            if 'subscribers' in node:
                                break
                                # Adds temporary interaction change

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
