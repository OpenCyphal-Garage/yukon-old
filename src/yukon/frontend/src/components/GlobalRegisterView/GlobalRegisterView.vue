<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div style="font-family: Roboto, Monospace;">
    <RegisterWorkset />

    <div class="subtle-border">
      <div class="row ml-2 fit-border mb-0">
        <h4>Legend</h4>
      </div>
      <div class="d-flex flex-row">
          <div class="p-2 immutable">Immutable</div>
          <div class="p-2 persistent">Persistent</div>
          <div class="p-2 mutable">Mutable</div>
          <div class="p-2 volatile">Volatile</div>
      </div>
    </div>

    <div class="d-flex flex-row">
      <h2 class="p-2 align-self-baseline">
        Filters
      </h2>

      <div class="p-2">
        <input v-model="registerNameFilter" class="form-control" type="text" placeholder="Register Name Filter" aria-label="Search">
      </div>

      <div class="p-2">
        <input v-model="nodeNameFilter" class="form-control" type="text" placeholder="Node Name Filter" aria-label="Search">
      </div>

      <div class="p-2">
        <input v-model="nodeIdFilter" class="form-control" type="text" placeholder="Node Id Filter" aria-label="Search">
      </div>

      <div class="p-2">
        <button type="button" class="btn btn-secondary" @click="clearFilters()">Clear</button>
      </div>
    </div>

    <div class="table-responsive global-register-view">
      <table class="table table-striped table-bordered table-sm" summary="Registers table">
        <thead>
          <th scope="registerName">full register name</th>
          <th scope="registerTree">tree</th>

          <th scope="node" v-for="node in Object.keys(nodeMapByName)" :key="node">
            {{ node }}
          </th>
        </thead>

        <tbody>
          <tr v-for="row in registerTableRows" :key="row.key">
            <td>{{ row.register === '' ? row.name + '.*' : row.register }}</td>

            <td v-bind:style="{ 'padding-left': (12 + (row.indent * 15)) + 'px'}">
              <div v-if="!row.leaf && (collapsedRegisters[row.namePart] === undefined || !collapsedRegisters[row.namePart].should)"
              style="display: inline;" class="clickable" @click="toggleCollapse(row.namePart)">&#8595;</div>
              <div v-if="!row.leaf && (collapsedRegisters[row.namePart] !== undefined && collapsedRegisters[row.namePart].should)"
              style="display: inline;" class="clickable" @click="toggleCollapse(row.namePart)">&#8594;</div>

               {{ row.name }}
            </td>

            <td v-for="(d, index) in row.data" :key="index"
            >
              <div v-if="d === undefined"> </div>
              <div v-else>
               <p style="display: inline-block;"
                class="mb-0 pb-0"
                v-bind:class="{ 'immutable': !d.mutable, 'persistent': d.persistent, 'mutable': d.mutable, 'volatile': !d.persistent }">
                {{ d.text }}
               </p>

              <a v-if="workset[row.register] && !workset[row.register].nodeIds.includes(getNodeIdFromIndex(index))"
                class="float-right clickable" @click="removeFromWorkset(index, row.register)">-</a>
              <a v-else
                class="float-right clickable" @click="addToWorkset(index, row.register)">+</a>
              </div>

            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <img alt="" :src="require('@/assets/under_construction.gif')"/>
  </div>
</template>

<script>
import TypeValue from '@/components/Dsdl/TypeValue'
import TypeEditForm from '@/components/Dsdl/TypeEditForm'
import RegisterWorkset from './RegisterWorkset'

import { mapState, mapGetters } from 'vuex'

export default {
  name: 'GlobalRegisterView',
  components: {
    TypeValue, // eslint-disable-line vue/no-unused-components
    TypeEditForm, // eslint-disable-line vue/no-unused-components
    RegisterWorkset
  },
  async mounted () {
    await this.loadData()
  },
  data () {
    return {
      error: '',
      nodeNameFilter: '',
      nodeIdFilter: '',
      registerNameFilter: '',
      collapsedRegisters: {}
    }
  },
  computed: {
    ...mapState({
      workset: state => state.grv.registerWorkset,
      registers: state => state.grv.globalRegisterView
    }),
    ...mapGetters({
      nodeMapByName: 'grv/nodeMapByName',
      nodeMapById: 'grv/nodeMapById'
    }),
    registerRows: function () {
      const self = this
      let tree = {}
      // filter based on node name and node id
      // construct registereter tree : leaf objects contain the full registereter name
      this.registers
        .filter(x => x.registerName.includes(this.registerNameFilter) || x.registerName.match(this.registerNameFilter))
        .filter(x => x.nodeName.includes(this.nodeNameFilter) || x.nodeName.match(this.nodeNameFilter))
        .filter(x => (x.nodeId + '').includes(this.nodeIdFilter) || (x.nodeId + '').match(this.nodeIdFilter))
        .forEach(element => {
          const registerNameParts = element.registerName.split('.')
          const registerNameTreeBranches = registerNameParts.slice(0, -1)

          // split on '.' (dots) and if the branch is non-existent, populate the tree
          let pos = tree
          registerNameTreeBranches.forEach(register => {
            if (pos[register] === undefined) {
              pos[register] = {}
            }

            pos = pos[register]
          })

          // if it's a leaf node, add the full registerName as a string (not as an 'object')
          pos[registerNameParts.slice(-1)[0]] = element.registerName
        })

      const numberOfNodes = Object.keys(this.nodeMapByName).length // used to avoid extra allocations on the 2d array

      let rows = []
      let row = -1

      function appendData (t, indent, rowNamePrefix) {
        row++
        for (const [_n, possibleLeaf] of Object.entries(t)) {
          const namePart = rowNamePrefix + (rowNamePrefix === '' ? '' : '.') + _n
          rows[row] = {
            name: _n,
            namePart: namePart,
            key: row + _n,
            indent: indent, // computed recursively, starting from 0
            data: new Array(numberOfNodes), // empty for non-leaf entries
            register: '',
            leaf: true
          }

          if (typeof possibleLeaf === 'object') {
            rows[row].leaf = false
            appendData(possibleLeaf, indent + 1, namePart)
          } else {
            const leaf = possibleLeaf

            // nodeMapByName is the register list, indexed by node name
            // for quick node[register name] lookup
            let i = 0
            for (const [_, node] of Object.entries(self.nodeMapByName)) { // eslint-disable-line no-unused-vars
              const payload = node[leaf]
              if (payload !== undefined) {
                rows[row].data[i++] = (payload.value === undefined && payload.value == null) ? { text: '' }
                  : {
                    text: self.truncatedValueDisplayOf(payload.value),
                    mutable: payload.mutable,
                    persistent: payload.persistent
                  }
              } else {
                i++ // empty column -- padding (leaf nodes only)
              }
            }
            rows[row].register = leaf
            row++
          }
        }
      }
      appendData(tree, 0, '')
      return rows
    },
    registerTableRows: function () {
      const collapsedRegisters = this.collapsedRegisters
      const rows = this.registerRows

      let targetIndent = 999 // rows below this level collapse

      function collapseFilter (row) {
        const collapse = collapsedRegisters[row.namePart]

        if (collapse !== undefined && collapse.should) { // flagged as should-collapse
          if (row.indent < targetIndent) { // if _not_ already collapsing from a lower indentation level
            targetIndent = row.indent // start collapsing from current indentaion level
          }

          return true // show current row so that we can un-collapse
        }

        // row not flagged for collapse
        // if on a lower indent, reset target indent
        if (row.indent <= targetIndent) {
          targetIndent = 999
        }

        const shouldCollapse = row.indent > targetIndent
        return !shouldCollapse
      }

      const ret = rows.filter(collapseFilter)
      return ret
    }
  },
  methods: {
    async loadData () {
      this.error = ''
      try {
        await this.$store.dispatch('grv/getGlobalRegisterView')
      } catch (e) {
        this.error = e
      }
    },
    truncatedValueDisplayOf (val) {
      return val // for now
    },
    toggleCollapse (namePart) {
      const currentState = this.collapsedRegisters[namePart]
      if (currentState === undefined) {
        this.collapsedRegisters[namePart] = {
          should: false
        }
      }

      const current = this.collapsedRegisters[namePart].should
      this.collapsedRegisters[namePart].should = !current
      this.collapsedRegisters = Object.assign({}, this.collapsedRegisters) // trigger watchers
    },
    clearFilters () {
      this.registerNameFilter = ''
      this.nodeNameFilter = ''
      this.nodeIdFilter = ''
    },
    getNodeIdFromIndex (nodeIndex) {
      const k = Object.keys(this.nodeMapByName)[nodeIndex]
      const node = this.nodeMapByName[k]
      return node.id
    },
    addToWorkset (nodeIndex, registerName) {
      const id = this.getNodeIdFromIndex(nodeIndex)
      this.$store.dispatch('grv/addNodeToWorkset', { id, registerName })
    },
    removeFromWorkset (nodeIndex, registerName) {
      const id = this.getNodeIdFromIndex(nodeIndex)
      this.$store.dispatch('grv/removeNodeFromWorkset', { id, registerName })
    }
  }
}
</script>

<style scoped>
@import '../../assets/styles/registers.css';
</style>
