/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import axios from 'axios'
import Vue from 'vue'
import ApiRoutes from '@/api/ApiRoutes'

const state = {
  typeInfo: {}
}

const getters = {
}

const actions = {
  async getTypeInfo ({commit}, type) {
    if (state.typeInfo[type]) {
      return // already working on retrieving type info
    }

    const cachedType = cache.get(type)
    if (cachedType) {
      commit('updateTypeInfo', { name: type, info: cachedType })
      return
    }

    state[type] = {}
    const response = await axios.get(ApiRoutes.Types.GetTypeInfoByName(type))
    const info = response.data

    const cacheHeader = response.headers['Cache-Control']

    if (cacheHeader && cacheHeader !== 'no-store') {
      if (cacheHeader.startsWith('max-age=')) {
        const duration = parseInt(cacheHeader.substring('max-age='.length, cacheHeader.length))

        if (!isNaN(duration)) {
          cache.save(name, info, duration)
        }
      }
    }

    commit('updateTypeInfo', { name: type, info: info })
  }
}

const mutations = {
  updateTypeInfo (state, { name, info }) {
    Vue.delete(state.typeInfo, name)
    Vue.set(state.typeInfo, name, info)
  }
}

const cache = {
  save (name, info, duration) {
    const validUntil = this.getTimestamp() + duration
    localStorage[this.keyFor(name)] = {
      info: info,
      validUntil: validUntil
    }
  },
  get (name, info) {
    const cachedValue = localStorage[this.keyFor(name)]
    if (cachedValue) {
      if (this.getTimestamp() < cachedValue.validUntil) {
        return cachedValue.info
      }
    }
    return undefined
  },
  keyFor (name) {
    return `type-${name}`
  },
  getTimestamp () {
    return Math.round(new Date().getTime() / 1000)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
