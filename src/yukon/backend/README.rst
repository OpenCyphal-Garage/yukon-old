################################################
Yukon Backend
################################################

* UAVCAN/Yukon Python backend
* Uses new asynchronous PyUAVCAN to provide a REST interface over a :code:`libuavcan` data bus
* Swagger Documentation provided

************************************************
Build
************************************************

    **Requires Python>=3.7**

To install from PyPi::

    pip3 install --user yukon_backend

To install from the requirements, use :code:`setup.py`::

    python3 setup.py install

************************************************
Usage
************************************************

Start the demo UAVCAN node::

    python3 uavcan_node_demo.py

Run server::

    python3 api/main.py

************************************************
Mock system and session
************************************************

It is possible to test the usage of the overall Yukon system with the usage of a mock server that provides the required inputs to simulate a system working over UAVCAN (static description), and a session of that system (runtime description, defined over a period of time).

The mock data is injected through the back-end :code:`devserv`, which data is described under using session and system description files (example can be found under the :code:`devserv/description/example directory`, and forwarded to the frontend using the Quart async calls, and routed/rendered by Vue.

:code:`mock_server.py` is a back-end Python script that allows loading the description for the system and session and and them send as response.

The default :code:`.json` file templates are provided inside description/templates directory. An example for the system mock description can be found in description/example.

The mock description current structure follows the following approach:

1. :code:`sys_description.json` has the information regarding the bus and nodes. The information regarding each node is provided by both the plu-and-play field but also through the nodes field, where each node detail can be consulted. Each node has its own description, identified with its ID, and the node information is stored inside those fields. Further node info, like register access, can be found inside the detail that corresponds to that specific node.

2. :code:`sess_description` has the correspondent log name to be created, followed by any runtime events that might happen which are not provided on the log and/or failure injections. Note that this description represents timed actions, which means that it requires any sort log generation and replay (**NOT AVAILABLE YET**). More info can be found in https://github.com/UAVCAN/pyuavcan/issues/74.

To test a mock input:

1. Inside the frontend folder, start the :code:`webpack-dev-server` with development configurations and without being served, run::

    npm run dev

2. Inside the backend folder, run::

    python3 src/devserv/mock_server.py

3. Open a browser window in http://localhost:8080.
