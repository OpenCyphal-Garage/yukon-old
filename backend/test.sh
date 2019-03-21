#!/bin/bash

status=0

# Static type checking
if ! mypy --strict --config-file=setup.cfg api test
then
    status=1
fi

# Code style checking
if ! pycodestyle --show-source api test
then
    status=1
fi

# Unit tests
if coverage run --source tests/ -m pytest --capture=no -vv api
then
    coverage report
else
    status=1
fi

exit $status
