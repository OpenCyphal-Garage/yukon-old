#!/usr/bin/env python3
#
# Copyright (C) 2019  UAVCAN Development Team  <uavcan.org>
#               2020  dronesolutions.io. All rights reserved.
# This software is distributed under the terms of the MIT License.
#

"""
.. module:: main
   :platform: Unix, Windows
   :synopsis: Runs the Yukon backend

.. moduleauthor:: Theodoros Ntakouris <zarkopafilis@gmail.com>
.. moduleauthor:: Nuno Marques <nuno.marques@dronesolutions.io>
"""

import sys

from asyncio import all_tasks, gather, get_event_loop, Task, sleep
from quart import Quart, render_template
from quart_cors import cors

# Controllers
from controllers.nodes import nodes_controller
from controllers.nodes import MonitorNode


async def main() -> int:
    """
        Start the backend Quart-based web server with CORS access control
    """
    backend = Quart(__name__,
                    static_folder='../../../frontend/static/',
                    template_folder='../../../frontend/')

    # Apply CORS access control headers to all routes in the backend
    backend = cors(backend)

    # Register endpoint modules
    backend.register_blueprint(nodes_controller, url_prefix='/api/v1/nodes')

    # Sink all undeclared routes so that vue can work with router properly
    @backend.route('/', defaults={'path': ''})
    @backend.route('/<path:path>')
    async def catch_all(path: str) -> str:
        return await render_template('index.html')

    return await backend.run_task(port=5000)

if __name__ == "__main__":
    loop = get_event_loop()
    monitor_node = MonitorNode(loop)
    try:
        sys.stdout.write('\n\033[92mDemo Backend process started!\n\033[0m')
        loop.run_until_complete(main())
        loop.close()
    except (KeyboardInterrupt, SystemExit):
        sys.stdout.write('\n\n\033[94mBackend process terminated!\n\033[0m')
        sys.exit(0)

