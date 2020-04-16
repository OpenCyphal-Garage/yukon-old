#####################
Contributor Notes
#####################

Hi! Thanks for contributing. This page contains all the details about getting
your dev environment setup.

.. note::

    This is documentation for contributors developing yukon. If you are
    a user of this software you can ignore everything here.

    - To ask questions about yukon or UAVCAN in general please see the `UAVCAN forum`_.
    - See `yukon on read the docs`_ for the full set of yukon documentation.
    - See the `UAVCAN website`_ for documentation on the UAVCAN protocol.

.. warning::

    When committing to master you **must** bump at least the patch number in ``src/yukon/backend/api/version.py``
    and in ``src/yukon/frontend/package.json`` or the build will fail on the upload step.


************************************************
Tools
************************************************

tox -e local
================================================

I highly recommend using the local tox environment when doing python development. It'll save you hours
of lost productivity the first time it keeps you from pulling in an unexpected dependency from your
global python environment. You can install tox from brew on osx or apt-get on linux. I'd
recommend the following environment for vscode::

    git submodule update --init --recursive
    tox -e local
    source .tox/local/bin/activate


Visual Studio Code
================================================

To use vscode you'll need:

1. vscode
2. install vscode commandline (`Shell Command: Install`)
3. tox

Do::

    cd path/to/yukon
    git submodule update --init --recursive
    tox -e local
    source .tox/local/bin/activate
    code .

Then install recommended extensions.

************************************************
Running The Tests
************************************************

To run the full suite of `tox`_ tests locally you'll need docker. Once you have docker installed
and running do::

    git submodule update --init --recursive
    docker pull uavcan/nodethon:node13-py37-py38
    docker run --rm -it -v $PWD:/repo uavcan/nodethon:node13-py37-py38
    tox


Sybil Doctest
================================================

This project makes extensive use of `Sybil <https://sybil.readthedocs.io/en/latest/>`_ doctests.
These take the form of docstrings with a structure like thus::

    .. invisible-code-block: python

        from yukon.lang.py import filter_to_snake_case

    .. code-block:: python

        # an input like this:
        input = "scotec.mcu.Timer"

        # should yield:
        filter_to_snake_case(input)
        >>> scotec_mcu_timer

The invisible code block is executed but not displayed in the generated documentation and,
conversely, ``code-block`` is both rendered using proper syntax formatting in the documentation
and executed. REPL works the same as it does for :mod:`doctest` but ``assert`` is also a valid
way to ensure the example is correct especially if used in a trailing ``invisible-code-block``::

    .. invisible-code-block: python

        assert 'scotec_mcu_timer' == filter_to_snake_case(input)

These tests are run as part of the regular pytest build. You can see the Sybil setup in the
``conftest.py`` found under the ``src`` directory but otherwise shouldn't need to worry about
it. The simple rule is; if the docstring ends up in the rendered documentation then your
``code-block`` tests will be executed as unit tests.


************************************************
Building The Docs
************************************************

We rely on `read the docs`_ to build our documentation from github but we also verify this build
as part of our tox build. This means you can view a local copy after completing a full, successful
test run (See `Running The Tests`_) or do
:code:`docker run --rm -t -v $PWD:/repo uavcan/nodethon:node13-py37-py38 /bin/sh -c "tox -e docs"` to build
the docs target. You can open the index.html under .tox/docs/tmp/index.html or run a local
web-server::

    python -m http.server --directory .tox/docs/tmp &
    open http://localhost:8000/index.html

Of course, you can just use `Visual Studio Code`_ to build and preview the docs using
:code:`> reStructuredText: Open Preview`.

apidoc
================================================

We manually generate the api doc using ``sphinx-apidoc``. To regenerate use ``tox -e gen-apidoc``.

.. warning::

    ``tox -e gen-apidoc`` will start by deleting the docs/api directory.


************************************************
Coverage and Linting Reports
************************************************

We publish the results of our coverage data to `sonarcloud`_ and the tox build will fail for any mypy
or flake8 errors but you can view additional reports locally under the :code:`.tox` dir.

Coverage
================================================

We generate a local html coverage report. You can open the index.html under .tox/report/tmp
or run a local web-server::

    python -m http.server --directory .tox/report/tmp &
    open http://localhost:8000/index.html

Mypy
================================================

At the end of the mypy run we generate the following summaries:

- .tox/mypy/tmp/mypy-report-lib/index.txt
- .tox/mypy/tmp/mypy-report-script/index.txt

************************************************
Buildkite on aws
************************************************

The PyPI upload keys should be rotated periodically. To do this you'll need to be an administrator of
our Buildkite `AWS CloudFormation`_ stack and of our PyPI UAVCAN organization.

    1. Download the buildkite-managedsecretsbucket-xxxxxxxx/yukon-release/env s3 artifact.
    2. In your PyPI account settings create a new API key scoped only to the yukon project and replace
       the one in the downloaded env file.
    3. Upload the modified env file::

        aws s3 cp --acl private --sse aws:kms ~/Downloads/env "s3://buildkite-managedsecretsbucket-xxxxxxxx/yukon-release/env"

    4. Back in the PyPI keys list delete any keys that are older than the one previously in use. You can keep the key
       you just rotated until you rotate the new key.

.. _`read the docs`: https://readthedocs.org/
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`sonarcloud`: https://sonarcloud.io/dashboard?id=UAVCAN_Yukon
.. _`UAVCAN website`: http://uavcan.org
.. _`UAVCAN forum`: https://forum.uavcan.org
.. _`yukon on read the docs`: https://yukon.readthedocs.io/en/latest/index.html
.. _`AWS CloudFormation`: https://aws.amazon.com/cloudformation/