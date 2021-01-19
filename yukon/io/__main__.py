# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import asyncio
from ._worker import IOWorker


if __name__ == "__main__":
    wrk = IOWorker()
    try:
        asyncio.get_event_loop().run_until_complete(wrk.run())
    finally:
        wrk.close()
