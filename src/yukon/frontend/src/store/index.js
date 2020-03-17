/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import Vue from 'vue'
import Vuex from 'vuex'
import general from './modules/general'
import nodes from './modules/nodes'
import types from './modules/types'
import grv from './modules/grv'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

export default new Vuex.Store({
  modules: {
    general,
    nodes,
    types,
    grv
  },
  strict: debug,
  plugins: debug ? [] : []
})
