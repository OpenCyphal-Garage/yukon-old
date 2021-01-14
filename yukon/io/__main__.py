# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

import click
import typing
import logging
import asyncio
import yukon.dcs
from org_uavcan_yukon.io.frame import Capture_0_1 as Capture
from org_uavcan_yukon.io.worker import Config_0_1 as Config
from org_uavcan_yukon.io.worker import Feedback_0_1 as Feedback
from org_uavcan_yukon.io.transport import SpoofedTransfer_0_1 as SpoofedTransfer


_logger = logging.getLogger(__name__)


@click.command()
@click.argument("dcs-transport-expression", required=True)
@click.option("--pub-capture-id-min-max", required=True, type=int, nargs=2)
@click.option("--pub-feedback-id", required=True, type=int)
@click.option("--sub-config-id", required=True, type=int)
@click.option("--sub-spoof-id", required=True, type=int)
def main(
    dcs_transport_expression: str,
    pub_capture_id_min_max: typing.Tuple[int, int],
    pub_feedback_id: int,
    sub_config_id: int,
    sub_spoof_id: int,
) -> None:
    """
    :param dcs_transport_expression:    How to connect with other DCS nodes.
    :param pub_capture_id_min_max:      Range of subject-ID where captured frames will be published.
    :param pub_feedback_id:             IO worker feedback (status report) subject.
    :param sub_config_id:               IO worker configuration subject.
    :param sub_spoof_id:                Transfers that are to be emitted by the IO workers submitted via this subject.
    """
    pub_frame_id_set = set(range(pub_capture_id_min_max[0], pub_capture_id_min_max[-1] + 1))
    other_list = [pub_feedback_id, sub_config_id, sub_spoof_id]
    if not pub_frame_id_set:
        raise ValueError("Frame subject-ID set is empty")
    if pub_frame_id_set & set(other_list) or len(set(other_list)) != len(other_list):
        raise ValueError("Conflicting subject-ID values")

    node = yukon.dcs.construct_node(dcs_transport_expression, "io")
    pubs_capture = [node.presentation.make_publisher(Capture, subject_id) for subject_id in pub_frame_id_set]
    pub_feedback = node.presentation.make_publisher(Feedback, pub_feedback_id)
    sub_config = node.presentation.make_subscriber(Config, sub_config_id)
    sub_spoof = node.presentation.make_subscriber(SpoofedTransfer, sub_spoof_id)

    _logger.info(f"Starting IO worker on DCS node {node} using ports:")
    _logger.info(f"- {pubs_capture[0]}")
    _logger.info(f"...<{len(pubs_capture) - 2} instances not shown, {len(pubs_capture)} total>...")
    _logger.info(f"- {pubs_capture[-1]}")
    _logger.info(f"- {pub_feedback}")
    _logger.info(f"- {sub_config}")
    _logger.info(f"- {sub_spoof}")
    from ._worker import run

    try:
        asyncio.get_event_loop().run_until_complete(run(node, pubs_capture, pub_feedback, sub_config, sub_spoof))
    finally:
        node.close()


if __name__ == "__main__":
    main()
