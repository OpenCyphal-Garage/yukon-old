#!/bin/bash

status=0

# Static type checking
if ! mypy --strict --config-file=setup.cfg api
then
    status=1
fi

# Code style checking
if ! pycodestyle --show-source api
then
    status=1
fi

# Unit tests
if coverage run --source api -m pytest --capture=no -vv api
then
    coverage report
else
    status=1
fi

exit $status
