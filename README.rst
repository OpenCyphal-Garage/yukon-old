################################################
Yukon
################################################

+--------------------------------+-----------------------------------+
| tox build (master)             | |badge_build|_                    |
+--------------------------------+-----------------------------------+
| static analysis                | |badge_analysis|_ |badge_issues|_ |
+--------------------------------+-----------------------------------+

An open suite of tools for observing, debugging, and interacting with a `UAVCAN`_ v1 bus.

************************************************
Installation & Development Instructions
************************************************

Install from Frontend::

    cd frontend
    npm install

Serve with hot reload at localhost::

    npm run dev

Build for production with minification::

    npm run build

Install backend::

    cd ../backend

Install dependencies::

    pip3 install quart quart_cors typing

Install documentation and testing dependencies::

    npm install mocha
    npm install jsdoc
    pip3 install sphinx sphinx-argparse sphinx-js sphinx_rtd_theme

Run server::

    python app.py


************************************************
Discussion
************************************************

Discussion takes part at the official `UAVCAN forum`_, specifically at `Yukon UI & Rest API`_ and `GUI Tool - Next Generation`_ forum threads.

************************************************
Backend Swagger Documentation
************************************************

- `Swaggerhub Api Docs Link`_

Most up to date swagger json is located at the `SWAGGERHUB` branch, under `/spec`. `swagger.json`_

.. _`UAVCAN`: http://uavcan.org
.. _`UAVCAN forum`:  https://forum.uavcan.org
.. _`Yukon UI & Rest API`: https://forum.uavcan.org/t/yukon-ui-rest-api/390/1
.. _`GUI Tool - Next Generation`: https://forum.uavcan.org/t/gui-tool-next-generation/229
.. _`Swaggerhub Api Docs Link`: https://app.swaggerhub.com/apis-docs/Zarkopafilis/Yukon/1.0.0
.. _`swagger.json`: https://github.com/UAVCAN/Yukon/blob/SWAGGERHUB/spec/swagger.json

.. |badge_build| image:: https://badge.buildkite.com/98867229c03fc1c66c05cfc9ecc1c29f597c7778957f53ac07.svg
    :alt: Build status
.. _badge_build: https://buildkite.com/uavcan/yukon-release

.. |badge_analysis| image:: https://sonarcloud.io/api/project_badges/measure?project=UAVCAN_Yukon&metric=alert_status
    :alt: Sonarcloud Quality Gate
.. _badge_analysis: https://sonarcloud.io/dashboard?id=UAVCAN_Yukon

.. |badge_issues| image:: https://sonarcloud.io/api/project_badges/measure?project=UAVCAN_Yukon&metric=bugs
    :alt: Sonarcloud bugs
.. _badge_issues: https://sonarcloud.io/dashboard?id=UAVCAN_Yukon