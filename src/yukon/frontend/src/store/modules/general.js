/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import axios from 'axios'
import ApiRoutes from '@/api/ApiRoutes'

const state = {
  serverHealth: {},
  busInfo: {}
}

const getters = {}

const actions = {
  async getServerHealth ({ commit }) {
    const response = await axios.get(ApiRoutes.General.Health)
    const nodes = response.data
    commit('setServerHealth', nodes)
  },
  async getBusInfo ({ commit }) {
    const response = await axios.get(ApiRoutes.Bus.GetInfo)
    const busInfo = response.data
    commit('setBusInfo', busInfo)
  }
}

const mutations = {
  setServerHealth (state, health) {
    state.serverHealth = health
  },
  setBusInfo (state, info) {
    state.busInfo = info
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
