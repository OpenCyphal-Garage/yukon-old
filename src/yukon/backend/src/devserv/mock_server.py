#!/usr/bin/env python3
#
# Copyright (C) 2019  UAVCAN Development Team  <uavcan.org>
#               2020  dronesolutions.io. All rights reserved.
# This software is distributed under the terms of the MIT License.
#

"""
.. automodule:: mock_server
   :platform: Unix, Windows
   :synopsis: Runs a backend mock server
   :members:

.. moduleauthor:: Nuno Marques <nuno.marques@dronesolutions.io>
"""

import os
import sys
import random
import argparse
import asyncio
import json
import threading
from quart import Quart, Response
from quart_cors import cors
from sched import scheduler
from time import sleep, time
from typing import Tuple
from typing import AsyncGenerator
from typing import Dict


dir_path = os.path.dirname(os.path.realpath(__file__))


def rename(newname: str):
    """
    Decorator to rename function name.
    Required since each Quart path requires a different function.
    """
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
            data=None,
            event=None
    ) -> None:
        self.data = data
        self.event = event

    def encode(self) -> bytes:
        """
        Encode response in JSON format.
        """
        message = f"data: {json.dumps(self.data)}"
        if self.event is not None:
            message = f"{message}\nevent: {self.event}"
        message = f"{message}\r\n\r\n"
        return message.encode('utf-8')


class MockLoader:
    """
    Class used to load mock system and description and present it to the frontend
    using both static paths and also time triggered events.
    """

    def __init__(self, sys_descr: str, sess_descr: str) -> None:
        self._api_prefix = '/api/v1'
        self._sys_descr = sys_descr
        self._sess_descr = sess_descr

        self._app = Quart(__name__,
                          static_folder='../../../frontend/static/',
                          template_folder='../../../frontend/')
        self._app = cors(self._app)
        self._session_timer_start = time()
        self._session_scheduler = scheduler(time, sleep)
        self._event = ServerSentEvent()

        self.load_mock_system_description()
        self.load_mock_session_description()

    @property
    def api_prefix(self) -> str:
        return self._api_prefix

    @property
    def app(self) -> Quart:
        return self._app

    @property
    def sys_descr(self) -> str:
        return self._sys_descr

    @property
    def sess_descr(self) -> str:
        return self._sess_descr

    @property
    def session_timer_start(self) -> time:
        return self._session_timer_start

    @property
    def session_scheduler(self) -> scheduler:
        return self._session_scheduler

    @property
    def event(self) -> ServerSentEvent:
        return self._event

    @event.setter
    def event(self, event):
        self._event = event

    def load_mock_system_description(self) -> Tuple[str, int]:
        """
        Loads mock system description from JSON file. The data is then split by
        the diferent components and loaded once, with each response sent to its
        specific path.
        """
        with open(os.path.join(dir_path, self.sys_descr + ".json")) as json_file:
            data = json.load(json_file)

            # Bus specific data. Gets rendered in the BusInfo component of the
            # Home page
            if 'bus' in data:
                @self.app.route(os.path.join(self.api_prefix, 'bus'))
                async def bus_mock() -> Tuple[str, int]:
                    return self.mock_response(self.sys_descr, data['bus'])

            # Node specific data. Gets rendered in the NodeList component of the
            # Home page but also on each node specific detail page.
            if 'nodes' in data:
                if data['nodes']['detail']:

                    # Rendered in the NodeList component
                    @self.app.route(os.path.join(self.api_prefix, 'nodes'))
                    async def nodes_mock() -> Tuple[str, int]:
                        return self.mock_response(self.sys_descr, data['nodes']['detail'])

                    for nodes in data['nodes']['detail']:
                        # Node detailed info
                        # Rendered in each node page (identified by its ID)
                        @self.app.route(os.path.join(self.api_prefix, 'nodes/' + str(nodes['id'])))
                        @rename('nodes_id' + str(nodes['id']) + '_mock()')
                        async def f() -> Tuple[str, int]:
                            return self.mock_response(self.sys_descr, data['nodes']['detail'][nodes['id']])

                        # Node assotiated registers
                        # Rendered in the Register table of each node page
                        if 'registers' in nodes:
                            @self.app.route(os.path.join(self.api_prefix, 'nodes/' + str(nodes['id']) + '/registers'))
                            @rename('nodes_id' + str(nodes['id']) + '_registers_mock()')
                            async def f() -> Tuple[str, int]:
                                return self.mock_response(self.sys_descr, data['nodes']['detail'][nodes['id']]['registers'])

                        # Node assotiated publishers
                        # Rendered in the Publishers table of each node page
                        if 'publishers' in nodes:
                            @self.app.route(os.path.join(self.api_prefix, 'nodes/' + str(nodes['id']) + '/publishers'))
                            @rename('nodes_id' + str(nodes['id']) + '_pub_mock()')
                            async def f() -> Tuple[str, int]:
                                return self.mock_response(self.sys_descr, data['nodes']['detail'][nodes['id']]['publishers'])

                        # Node assotiated subscribers
                        # Rendered in the Subscribers table of each node page
                        if 'subscribers' in nodes:
                            @self.app.route(os.path.join(self.api_prefix, 'nodes/' + str(nodes['id']) + '/subscribers'))
                            @rename('nodes_id' + str(nodes['id']) + '_sub_mock()')
                            async def f() -> Tuple[str, int]:
                                return self.mock_response(self.sys_descr, data['nodes']['detail'][nodes['id']]['subscribers'])

                # Rendered in the Plug&Play table in the Home page
                # Note: currently hidden
                if data['nodes']['plugandplay']:
                    @self.app.route(os.path.join(self.api_prefix, 'nodes/plugandplay'))
                    async def plugandplay_mock() -> Tuple[str, int]:
                        return self.mock_response(self.sys_descr, data['nodes']['plugandplay'])

                # Rendered in the GlobalRegisterView page
                # Note: needs further improvements
                if data['nodes']['grv']:
                    @self.app.route(os.path.join(self.api_prefix, 'nodes/grv'))
                    async def global_register_view_mock() -> Tuple[str, int]:
                        return self.mock_response(self.sys_descr, data['nodes']['grv'])

            # Backend server health information
            # Rendered in the ServerHealth component of the Home page
            if 'health' in data:
                @self.app.route(os.path.join(self.api_prefix, 'health'))
                async def health_mock() -> Tuple[str, int]:
                    return self.mock_response(self.sys_descr, data['health'])

            # Data Type information
            # Note: needs further improvement and assotiation to the PRDT
            if 'types' in data:
                @self.app.route(os.path.join(self.api_prefix, 'types'))
                async def types_mock() -> Tuple[str, int]:
                    return self.mock_response(self.sys_descr, data['types'])

    def load_mock_session_description(self) -> Tuple[str, int]:
        """
        Load session description. This loads the time triggered events,
        which dynamically affect the visuals on the GUI canvas.
        """
        with open(os.path.join(dir_path, self.sess_descr + ".json")) as json_file:
            description = json.load(json_file)

            # The event scheduler assotiates an event to the timestamp
            # where it gets triggered.
            # Launched as a separate thread so to run in parallel with
            # the SSE asynchronous calls.
            event_scheduler_th = threading.Thread(
                target=self.event_scheduler, args=(description,))
            event_scheduler_th.daemon = True
            event_scheduler_th.start()

            @self.app.route(self.api_prefix + '/eventSource')
            async def sse_node_update() -> Tuple[AsyncGenerator[bytes, None], Dict[str, str]]:
                """
                Establishes a central co-routine that updates at a defined
                rate and sends server generated events at each iteration.
                The specific event to be sent depends on what the event
                scheduler thread defines, according to the defined timestamps
                on the session description.
                """
                async def send_event(rate) -> AsyncGenerator[bytes, None]:
                    while True:
                        await asyncio.sleep(1 / rate)
                        yield self.event.encode()

                return Response(send_event(30.0), mimetype="text/event-stream")

    def mock_response(self, path: str, elem: json) -> Tuple[str, int]:
        """
        Generates the reponse in a stringified JSON format.
        """
        response = json.dumps(elem)
        if response:
            return (response, 200)
        else:
            return ('', 404)

    def sse_builder(self, data, event_type) -> None:
        """
        Generates the SSE reponse in a JSON format.
        """
        self.event = ServerSentEvent(
            data=data, event=event_type)

    def event_scheduler(self, description) -> None:
        """
        Schedule events according to the defined timestamps
        in each event of the session description.
        """
        if 'events' in description:
            for event in description['events']:
                # Set the time when the session starts WRT to the start of the
                # Python mock server
                session_start = 0.0
                if event['starts_in']:
                    session_start = event['starts_in']

                # Events assotiated to the nodes
                if event['nodes']:
                    for idx, node in enumerate(event['nodes']):
                        node_event = event['nodes'][node]

                        # Node status change event
                        if 'status' in node_event:
                            status_event = node_event['status']

                            data = {
                                "id": int(node),
                                "health": status_event['health'],
                                "active": 1
                            }

                            # node appears
                            if 'timestamp_start' in status_event and status_event['timestamp_start']:
                                self.session_scheduler.enter(
                                    status_event['timestamp_start'], 1, self.sse_builder, [data, 'NODE_STATUS'])

                            # node disappears
                            if 'timestamp_end' in status_event and status_event['timestamp_end']:
                                data[idx]['active'] = 0

                                self.session_scheduler.enter(
                                    status_event['timestamp_end'], 1, self.sse_builder, [data, 'NODE_STATUS'])

                        # Node publishers changes
                        # Currently only simulates adding or removing; no rate
                        # assotiated events
                        if 'publishers' in node_event:
                            data = {
                                "id": int(node),
                                "publishers": []
                            }

                            for idx2, pub in enumerate(node_event['publishers']):
                                data['publishers'].append(pub)
                                data['publishers'][idx2].update(
                                    {"active": 1})

                                # subject line appears (assuming there's a corresponding subscriber)
                                if 'timestamp_start' in pub and pub['timestamp_start']:
                                    self.session_scheduler.enter(
                                        pub['timestamp_start'], 1, self.sse_builder, [data, 'NODE_STATUS'])

                                # subject line disappears
                                if 'timestamp_end' in pub and pub['timestamp_end']:
                                    data['publishers'][idx2].update(
                                        {"active": 0})

                                    self.session_scheduler.enter(
                                        pub['timestamp_end'], 1, self.sse_builder, [data, 'NODE_STATUS'])

                        # Node subscribers changes
                        # Currently only simulates adding or removing
                        if 'subscribers' in node_event:
                            data = {
                                "id": int(node),
                                "subscribers": []
                            }

                            for idx2, sub in enumerate(node_event['subscribers']):
                                data['subscribers'].append(sub)
                                data['subscribers'][idx2].update(
                                    {"active": 1})

                                # subject line appears (assuming there's a corresponding publisher)
                                if 'timestamp_start' in sub and sub['timestamp_start']:
                                    self.session_scheduler.enter(
                                        sub['timestamp_start'], 1, self.sse_builder, [data, 'NODE_STATUS'])

                                # subject line disappears
                                if 'timestamp_end' in sub and sub['timestamp_end']:
                                    self.session_scheduler.enter(
                                        sub['timestamp_end'], 1, self.sse_builder, [data, 'NODE_STATUS'])

        # Waits for a defined amount of seconds before starting the session
        while True:
            if ((time() - self._session_timer_start) >= session_start):
                sys.stdout.write('\033[34mMock session started...\n\033[0m')
                self.session_scheduler.run()
                break


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
