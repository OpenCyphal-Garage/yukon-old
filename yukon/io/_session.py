# Copyright (C) 2021  UAVCAN Consortium  <uavcan.org>
# This software is distributed under the terms of the MIT License.
# Author: Pavel Kirienko <pavel@uavcan.org>

from pyuavcan.transport import AlienSessionSpecifier
from org_uavcan_yukon.io.transfer import Session_0_1 as Session


def to_dcs_session(ses: AlienSessionSpecifier) -> Session:
    import uavcan.node.port
    from org_uavcan_yukon.io.transfer import SubjectSession_0_1 as SubjectSession
    from org_uavcan_yukon.io.transfer import ServiceSession_0_1 as ServiceSession
    from pyuavcan.transport import MessageDataSpecifier, ServiceDataSpecifier

    if isinstance(ses.data_specifier, MessageDataSpecifier):
        if ses.destination_node_id is not None:
            raise ValueError(f"Session not representable: {ses}")  # pragma: no cover
        return Session(
            subject=SubjectSession(
                subject_id=uavcan.node.port.SubjectID_1_0(ses.data_specifier.subject_id),
                source=[uavcan.node.ID_1_0(ses.source_node_id)] if ses.source_node_id is not None else [],
            )
        )

    if isinstance(ses.data_specifier, ServiceDataSpecifier):
        if ses.source_node_id is None or ses.destination_node_id is None:
            raise ValueError(f"Session not representable: {ses}")
        return Session(
            service=ServiceSession(
                service_id=uavcan.node.port.ServiceID_1_0(ses.data_specifier.service_id),
                source=uavcan.node.ID_1_0(ses.source_node_id),
                destination=uavcan.node.ID_1_0(ses.destination_node_id),
                is_request=ses.data_specifier.role == ServiceDataSpecifier.Role.REQUEST,
            )
        )

    assert False


def from_dcs_session(ses: Session) -> AlienSessionSpecifier:
    from pyuavcan.transport import MessageDataSpecifier, ServiceDataSpecifier

    if ses.subject:
        try:
            source_node_id = ses.subject.source[0].value
        except LookupError:
            source_node_id = None
        return AlienSessionSpecifier(
            source_node_id=source_node_id,
            destination_node_id=None,
            data_specifier=MessageDataSpecifier(subject_id=ses.subject.subject_id.value),
        )

    if ses.service:
        return AlienSessionSpecifier(
            source_node_id=ses.service.source.value,
            destination_node_id=ses.service.destination.value,
            data_specifier=ServiceDataSpecifier(
                service_id=ses.service.service_id.value,
                role=ServiceDataSpecifier.Role.REQUEST
                if ses.service.is_request
                else ServiceDataSpecifier.Role.RESPONSE,
            ),
        )

    assert False


def _unittest_session_spec() -> None:
    import pytest
    from pyuavcan.transport import MessageDataSpecifier, ServiceDataSpecifier

    ss = AlienSessionSpecifier(
        source_node_id=None,
        destination_node_id=None,
        data_specifier=MessageDataSpecifier(6666),
    )
    assert from_dcs_session(to_dcs_session(ss)) == ss

    ss = AlienSessionSpecifier(
        source_node_id=123,
        destination_node_id=None,
        data_specifier=MessageDataSpecifier(6666),
    )
    assert from_dcs_session(to_dcs_session(ss)) == ss

    ss = AlienSessionSpecifier(
        source_node_id=123,
        destination_node_id=321,
        data_specifier=ServiceDataSpecifier(222, ServiceDataSpecifier.Role.REQUEST),
    )
    assert from_dcs_session(to_dcs_session(ss)) == ss

    ss = AlienSessionSpecifier(
        source_node_id=123,
        destination_node_id=321,
        data_specifier=ServiceDataSpecifier(222, ServiceDataSpecifier.Role.RESPONSE),
    )
    assert from_dcs_session(to_dcs_session(ss)) == ss

    with pytest.raises(ValueError):
        to_dcs_session(
            AlienSessionSpecifier(
                source_node_id=None,
                destination_node_id=None,
                data_specifier=ServiceDataSpecifier(222, ServiceDataSpecifier.Role.RESPONSE),
            )
        )
