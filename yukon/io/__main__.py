# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import click
import logging
import asyncio
import yukon.dcs
from org_uavcan_yukon.io.frame import Capture_0_1 as Capture
from org_uavcan_yukon.io import Config_0_1 as Config
from org_uavcan_yukon.io import Status_0_1 as Status
from org_uavcan_yukon.io.transfer import Spoof_0_1 as Spoof


_logger = logging.getLogger(__name__)


@click.command()
@click.argument("dcs-transport-expression", required=True)
@click.option("--pub-capture-id", required=True, type=int)
@click.option("--pub-status-id", required=True, type=int)
@click.option("--sub-config-id", required=True, type=int)
@click.option("--sub-spoof-id", required=True, type=int)
def main(
    dcs_transport_expression: str,
    pub_capture_id: int,
    pub_status_id: int,
    sub_config_id: int,
    sub_spoof_id: int,
) -> None:
    """
    :param dcs_transport_expression:    How to connect with other DCS nodes.
    :param pub_capture_id:              Captured frame subject.
    :param pub_status_id:               IO subsystem status (status report) subject.
    :param sub_config_id:               IO subsystem configuration subject.
    :param sub_spoof_id:                Transfers that are to be emitted by the IO workers submitted via this subject.
    """
    if len({pub_capture_id, pub_status_id, sub_config_id, sub_spoof_id}) != 4:
        raise ValueError("Conflicting subject-ID values")

    node = yukon.dcs.Node(dcs_transport_expression, "io")
    pub_capture = node.presentation.make_publisher(Capture, pub_capture_id)
    pub_status = node.presentation.make_publisher(Status, pub_status_id)
    sub_config = node.presentation.make_subscriber(Config, sub_config_id)
    sub_spoof = node.presentation.make_subscriber(Spoof, sub_spoof_id)

    _logger.info(f"Starting IO worker on DCS node {node} using ports:")
    _logger.info(f"- {pub_capture}")
    _logger.info(f"- {pub_status}")
    _logger.info(f"- {sub_config}")
    _logger.info(f"- {sub_spoof}")
    from ._worker import IOWorker

    try:
        wrk = IOWorker(node, pub_capture, pub_status, sub_config, sub_spoof)
        asyncio.get_event_loop().run_until_complete(wrk.run())
    finally:
        node.close()


if __name__ == "__main__":
    main()
