import axios from 'axios'
import Vue from 'vue'
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
  addNodeToWorkset ({ commit }, payload) {
    commit('addToWorkset', payload)
  },
  removeNodeFromWorkset ({commit}, payload) {
    commit('removeFromWorkset', payload)
  },
  removeRegisterFromWorkset ({commit}, register) {
    commit('removeWorkset', register)
  }
}

const mutations = {
  setGlobalRegisterView (state, grv) {
    state.globalRegisterView = grv
  },
  removeWorkset (state, register) {
    Vue.delete(state.registerWorkset, register)
  },
  addToWorkset (state, {id: nodeId, registerName}) {
    const member = state.registerWorkset[registerName]
    if (member === undefined) {
      Vue.set(state.registerWorkset, registerName, {
        nodeIds: [nodeId],
        type: getters.nodeMapById()[nodeId][registerName].value._type_
      })
      return
    }

    if (member.nodeIds.includes(nodeId)) {
      return
    }

    state.registerWorkset[registerName].nodeIds = member.nodeIds.push(nodeId)
  },
  removeFromWorkset (state, {id: nodeId, registerName}) {
    let member = state.registerWorkset[registerName]
    if (member === undefined) {
      // should not happen / ignore
      return
    }

    const newMembers = member.nodeIds.filter(e => e !== nodeId)
    console.log(newMembers)

    state.registerWorkset[registerName].nodeIds = newMembers

    if (newMembers.length === 0) {
      Vue.delete(state.registerWorkset, registerName)
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
