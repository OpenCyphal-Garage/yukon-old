#!/usr/bin/env python3
#
# Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
#
# Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
#

# App, Static, Templates folder, CORS setup
# Controller wiring

import quart
from quart import Quart, render_template
from quart_cors import cors
# Controllers
from controllers.nodes import nodes_controller
from controllers.nodes import MonitorNode

import asyncio

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    monitor_node = MonitorNode(loop)

    app = Quart(__name__,
                static_folder='../../../frontend/static/',
                template_folder='../../../frontend/')
    app = cors(app)

    api_prefix = '/api/v1'

    # Register endpoint modules
    app.register_blueprint(nodes_controller, url_prefix=api_prefix + '/nodes')

    # Sink all undeclared routes so that vue can work with router properly
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    async def catch_all(path: str) -> str:
        return await render_template('index.html')

    loop.run_until_complete(app.run_task(port=5000))
    loop.close()



