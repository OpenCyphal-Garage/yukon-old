#!/usr/bin/env bash
#
# Copyright (C) 2020  UAVCAN Development Team  <uavcan.org>
#               2020  dronesolutions.io. All rights reserved.
# This software is distributed under the terms of the MIT License.
#

# +----------------------------------------------------------+
# | BASH : Modifying Shell Behaviour
# |    (https://www.gnu.org/software/bash/manual)
# +----------------------------------------------------------+
# Treat unset variables and parameters other than the special
# parameters ‘@’ or ‘*’ as an error when performing parameter
# expansion. An error message will be written to the standard
# error, and a non-interactive shell will exit.
set -o nounset

# Exit immediately if a pipeline returns a non-zero status.
set -o errexit

# If set, the return value of a pipeline is the value of the
# last (rightmost) command to exit with a non-zero status, or
# zero if all commands in the pipeline exit successfully.
set -o pipefail

# +----------------------------------------------------------+

# Get the Backend and Frontend versions
export YUKON_BACKEND_FULL_VERSION=$(grep __version__ src/yukon/backend/src/api/version.py | sed -E "s/'([0-9]+\.[0-9]+\.[0-9]+)'/\1/g")
export YUKON_FRONTEND_FULL_VERSION=$(node -e "console.log(require('./src/yukon/frontend/package.json').version);")
export YUKON_BACKEND_MAJOR_MINOR_VERSION=$(echo $YUKON_BACKEND_FULL_VERSION | sed -E "s/([0-9]+\.[0-9]+)\.[0-9]+/\1/g")
export YUKON_FRONTEND_MAJOR_MINOR_VERSION=$(echo $YUKON_FRONTEND_FULL_VERSION | sed -E "s/([0-9]+\.[0-9]+)\.[0-9]+/\1/g")
tox
tox -e sonar | grep -v "sonar.login"
# Upload yukon_backend to PyPi
tox -e pypi_upload | grep -v "twine upload"
# Only publish yukon_frontend to npm if the version is different from the one already published (otherwise it will fail)
if [[ $YUKON_FRONTEND_FULL_VERSION != $(npm view yukon_frontend version) ]]; then
  tox -e npm_publish | grep -v "npm publish"
fi
