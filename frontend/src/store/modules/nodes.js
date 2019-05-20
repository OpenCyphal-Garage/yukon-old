import axios from 'axios'
import ApiRoutes from '@/api/ApiRoutes'

const state = {
  nodeList: [],
  plugAndPlayTable: {}
}

const getters = {}

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
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
