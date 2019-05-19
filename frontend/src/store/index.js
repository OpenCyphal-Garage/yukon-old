import Vue from 'vue'
import Vuex from 'vuex'
import general from './modules/general'
import nodes from './modules/nodes'
import types from './modules/types'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

export default new Vuex.Store({
  modules: {
    general,
    nodes,
    types
  },
  strict: debug,
  plugins: debug ? [] : []
})
