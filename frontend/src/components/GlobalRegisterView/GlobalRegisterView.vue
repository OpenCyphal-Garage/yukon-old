<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div>
    <div class="subtle-border">
      <div class="row ml-2 fit-border mb-0">
        <h4>Workset</h4>
      </div>
      <div class="ml-2">
        <!-- For each register in the workset -->
        <div class="row m-0 col-12" v-for="reg in Object.keys(workset)" :key="reg">
          <h5 class="ml-1 col-12 text-left">~ {{ reg }}</h5>
          <!-- For node with that register -->
          <div class="col-12 text-left ml-2 pb-2" v-for="id in workset[reg].nodeIds" :key="reg + ':' + id">
              <h6 class="ml-2">- {{ nodeMapById[id].name + '  ' + '[' + id + ']'}} -></h6>
              <TypeValue class="ml-4" v-bind:val="valueOf(id, reg)" />
          </div>
        </div>
      </div>
    </div>

    <div class="subtle-border">
      <div class="row ml-2 fit-border mb-0">
        <h4>Register Edit</h4>
      </div>
      <div class="row m-0 col-12 text-left pb-2" v-if="Object.keys(workset).length > 0">
          <TypeEditForm v-bind:type="firstKeyOf(workset).type"/>
      </div>
    </div>

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
      <table class="table table-striped table-bordered table-sm">
        <thead>
          <th>full register name</th>
          <th>tree</th>

          <th v-for="node in Object.keys(nodeMap)" :key="node">
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
              <div v-else v-bind:class="{ 'immutable': !d.mutable, 'persistent': d.persistent, 'mutable': d.mutable, 'volatile': !d.persistent }"
              > {{ d.text }} </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import TypeValue from '@/components/Dsdl/TypeValue'
import TypeEditForm from '@/components/Dsdl/TypeEditForm'
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'GlobalRegisterView',
  components: {
    TypeValue,
    TypeEditForm
  },
  async mounted () {
    await this.loadData()
  },
  data () {
    return {
      error: '',
      workset: {
        'uavcan.a.b.1': {
          nodeIds: [0],
          type: 'uavcan.register.Access.Request'
        }
      },
      nodeNameFilter: '',
      nodeIdFilter: '',
      registerNameFilter: '',
      collapsedRegisters: {}
    }
  },
  computed: {
    ...mapState({
      registers: state => state.grv.globalRegisterView
    }),
    ...mapGetters({
      nodeMap: 'grv/nodeMap',
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

      const numberOfNodes = Object.keys(this.nodeMap).length // used to avoid extra allocations on the 2d array

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

            // nodeMap is the register list, indexed by node name
            // for quick node[register name] lookup
            let i = 0
            for (const [_, node] of Object.entries(self.nodeMap)) { // eslint-disable-line no-unused-vars
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
    firstKeyOf (obj) {
      return obj[Object.keys(obj)[0]]
    },
    valueOf (nodeId, registerName) {
      const n = this.nodeMapById[nodeId]
      if (n === undefined) {
        return undefined
      }

      return n[registerName]
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
    }
  }
}
</script>

<style scoped>
@import '../../assets/styles/registers.css';
</style>
