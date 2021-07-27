# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import sys
import asyncio
import logging
from ._worker import IOWorker


if __name__ == "__main__":
    wrk = IOWorker()
    try:
        logging.info("IO worker started")
        result = asyncio.get_event_loop().run_until_complete(wrk.run())
    except KeyboardInterrupt:
        result = 0
    except Exception as ex:
        logging.critical("Process failed: %s", ex, exc_info=True)
        result = -1
    finally:
        wrk.close()
    sys.exit(result)
