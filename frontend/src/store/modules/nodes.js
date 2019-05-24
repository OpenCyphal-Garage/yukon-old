/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import axios from 'axios'
import ApiRoutes from '@/api/ApiRoutes'

const state = {
  nodeList: [],
  plugAndPlayTable: {}
}

const getters = {
  statusOf: state => (nodeId) => {
    return state.nodeList.find(node => node.id === nodeId)
  }
}

const actions = {
  async getNodeList ({ commit }) {
    const response = await axios.get(ApiRoutes.Nodes.GetAll)
    const nodes = response.data
    commit('setNodeList', nodes)
  },
  async getPlugAndPlayTable ({ commit }) {
    const response = await axios.get(ApiRoutes.Nodes.GetPlugAndPlayTable)
    const table = response.data
    commit('setPlugAndPlayTable', table)
  }
}

const mutations = {
  setNodeList (state, nodeList) {
    state.nodeList = nodeList
  },
  setPlugAndPlayTable (state, table) {
    state.plugAndPlayTable = table
  },
  updateNodeStatus (state, newNodeStatus) {
    const target = state.nodeList.find(node => node.id === newNodeStatus.id)

    if (!target) {
      state.nodeList.push(newNodeStatus)
      return
    }

    for (const key in newNodeStatus) {
      if (key === 'id') {
        continue
      }

      target[key] = newNodeStatus[key]
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
