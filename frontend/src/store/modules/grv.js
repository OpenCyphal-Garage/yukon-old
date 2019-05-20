import axios from 'axios'
import ApiRoutes from '@/api/ApiRoutes'

const state = {
  globalRegisterView: [],
  registerWorkset: {}
}

const getters = {
  nodeMapByName: function () {
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
  },
  addRegisterToWorkset ({ commit }, payload) {
    commit('addToWorkset', payload)
  },
  removeRegisterFromWorkset ({commit}, payload) {
    commit('removeFromWorkset', payload)
  }
}

const mutations = {
  setGlobalRegisterView (state, grv) {
    state.globalRegisterView = grv
  },
  addToWorkset (state, {id: nodeId, registerName}) {
    const member = state.registerWorkset[registerName]
    if (member === undefined) {
      state.registerWorkset[registerName] = {
        nodeIds: [nodeId],
        type: getters.nodeMapById()[nodeId][registerName].value._type_
      }
      return
    }

    member.nodeIds.push(nodeId)
  },
  removeFromWorkset (state, {id: nodeId, registerName}) {
    let member = state.registerWorkset[registerName]
    if (member === undefined) {
      return
    }

    member.nodeIds = member.nodeIds.filter(e => e !== nodeId)

    if (member.nodeIds.length === 0) {
      state.registerWorkset[registerName] = undefined
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
