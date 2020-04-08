#!/usr/bin/env python3
#
# Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
# This software is distributed under the terms of the MIT License.
#
# Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
#

# App, Static, Templates folder, CORS setup
# Controller wiring

from quart import Quart, render_template
from quart_cors import cors
# Controllers
from .controllers.nodes import nodes_controller

api_prefix = '/api/v1'

app = Quart(__name__,
            static_folder='../../frontend/dist/static',
            template_folder='../../frontend/dist')
app = cors(app)

# Register endpoint modules
app.register_blueprint(nodes_controller, url_prefix=api_prefix + '/nodes')


# Sink all undeclared routes so that vue can work with router properly
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def catch_all(path: str) -> str:
    return await render_template('index.html')

if __name__ == "__main__":
    app.run(port=5000)
