import axios from 'axios'
import ApiRoutes from '@/api/ApiRoutes'

const state = {
  globalRegisterView: []
}

const getters = {
  nodeMap: function () {
    let nodes = {}

    state.globalRegisterView.forEach(element => {
      if (nodes[element.nodeName] === undefined) {
        nodes[element.nodeName] = {
          id: element.nodeId
        }
      }

      nodes[element.nodeName][element.registerName] = {
        value: element.value,
        mutable: element.mutable,
        persistent: element.persistent
      }
    })

    return nodes
  },
  nodeMapById: function () {
    let nodes = {}

    state.globalRegisterView.forEach(element => {
      if (nodes[element.nodeId] === undefined) {
        nodes[element.nodeId] = {
          name: element.nodeName
        }
      }

      nodes[element.nodeId][element.registerName] = {
        value: element.value,
        mutable: element.mutable,
        persistent: element.persistent
      }
    })

    return nodes
  }
}

const actions = {
  async getGlobalRegisterView ({ commit }) {
    const response = await axios.get(ApiRoutes.Nodes.GetGlobalRegisterView)
    const grv = response.data
    commit('setGlobalRegisterView', grv)
  }
}

const mutations = {
  setGlobalRegisterView (state, grv) {
    state.globalRegisterView = grv
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
