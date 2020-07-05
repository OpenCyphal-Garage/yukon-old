/**
 * Copyright (C) 2020 UAVCAN Development Team <uavcan.org>
 *               2020  dronesolutions.io. All rights reserved.
 * This software is distributed under the terms of the MIT License.
 *
 * @file SSE handler for subject publishing status updates
 * @author Nuno Marques <nuno.marques@dronesolutions.io>
 **/

import store from '@/store'

const subjectPubStatus = {
  eventType: 'SUBJECT_PUB_STATUS',
  handle: function (event) {
    const parsed = JSON.parse(event.data)
    store.commit('nodes/updateNodePublishers', parsed)
  }
}

export default subjectPubStatus
