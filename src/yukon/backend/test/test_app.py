#!/usr/bin/env python3
#
# Copyright (C) 2020  UAVCAN Development Team  <uavcan.org>
#               2020  dronesolutions.io. All rights reserved.
# This software is distributed under the terms of the MIT License.
#

from src.devserv.mock_responses import ServerSentEvent
import pytest


@pytest.mark.parametrize('event', [('test_event')])
def test_serverevent(event):
    sse = ServerSentEvent("test", event)
    assert sse.event == "test_event"
