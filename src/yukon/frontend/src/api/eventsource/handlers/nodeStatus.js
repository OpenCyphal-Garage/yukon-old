/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import store from '@/store'

const nodeStatus = {
  eventType: 'NODE_STATUS',
  handle: function (event) {
    const parsed = JSON.parse(event.data)
    store.commit('nodes/updateNodeStatus', parsed)
  }
}

export default nodeStatus
