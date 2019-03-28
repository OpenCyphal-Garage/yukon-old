<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div>
    <div class="table-responsive global-register-view">
      <table class="table table-striped table-bordered">
        <thead>
          <th>tree</th>
          <th v-for="node in nodeMap" :key="node.name">
            {{ node.name }}
          </th>

          <th>full register name</th>
        </thead>

        <tbody>
          <tr v-for="row in registerTableRows" :key="row.key">

            <td v-bind:style="{ 'padding-left': (12 + (row.indent * 15)) + 'px'}">
              <div v-if="!row.leaf && (collapsedRegisters[row.namePart] === undefined || !collapsedRegisters[row.namePart].should)" style="display: inline;" class="clickable" @click="toggleCollapse(row.namePart)">&#8595;</div>
              <div v-if="!row.leaf && (collapsedRegisters[row.namePart] !== undefined && collapsedRegisters[row.namePart].should)" style="display: inline;" class="clickable" @click="toggleCollapse(row.namePart)">&#8594;</div>

               {{ row.name }}
            </td>

            <td v-for="(d, index) in row.data" :key="index"> {{ d }}</td>
            <td>{{ row.register }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GlobalRegisterView',
  data () {
    return {
      registers: [
        {
          nodeId: 0,
          nodeName: 'esc0',
          registerName: 'uavcan.a.b',
          value: 'asdf'
        },
        {
          nodeId: 1,
          nodeName: 'esc1',
          registerName: 'uavcan.a.b',
          value: 'ghjk'
        },
        {
          nodeId: 2,
          nodeName: 'esc2',
          registerName: 'uavcan.a.b',
          value: 'qwer'
        },
        {
          nodeId: 3,
          nodeName: 'esc3',
          registerName: 'uavcan.a.b',
          value: 'tyui'
        },
        {
          nodeId: 0,
          nodeName: 'esc0',
          registerName: 'uavcan.a.something',
          value: 0
        },
        {
          nodeId: 0,
          nodeName: 'esc0',
          registerName: 'other.whatever',
          value: [4, 7, 9]
        },
        {
          nodeId: 4,
          nodeName: 'gps',
          registerName: 'uavcan.gps.a',
          value: 1
        },
        {
          nodeId: 4,
          nodeName: 'gps',
          registerName: 'uavcan.gps.b',
          value: 2
        },
        {
          nodeId: 4,
          nodeName: 'gps',
          registerName: 'other.whatever',
          value: [0, 1, 2, 3]
        },
        {
          nodeId: 4,
          nodeName: 'gps',
          registerName: 'other.uart_on',
          value: true
        }],
      collapsedRegisters: {}
    }
  },
  computed: {
    nodeMap: function () {
      let nodes = {}

      this.registers.forEach(element => {
        if (nodes[element.nodeName] === undefined) {
          nodes[element.nodeName] = {
            name: element.nodeName
          }
        }

        nodes[element.nodeName][element.registerName] = {
          value: element.value
        }
      })

      return nodes
    },
    registerRows: function () {
      const self = this
      let tree = {}
      // construct registereter tree : leaf objects contain the full registereter name
      this.registers.forEach(element => {
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
                rows[row].data[i++] = payload.value === undefined && payload.value != null ? '' : payload.value
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
          console.log(`collapsing: --- ${row.namePart}`)
          if (row.indent < targetIndent) { // if _not_ already collapsing from a lower indentation level
            targetIndent = row.indent // start collapsing from current indentaion level
          }

          return true // show current row so that we can un-collapse
        }

        // row not flagged for collapse
        // if on a lower indent, reset target indent
        if (row.indent <= targetIndent) {
          targetIndent = 999
          console.log(`reseting indent target: --- ${row.namePart}`)
        }

        const shouldCollapse = row.indent > targetIndent
        console.log(`${row.namePart} -- Visibility: ${!shouldCollapse}`)
        return !shouldCollapse
      }

      const ret = rows.filter(collapseFilter)
      console.log(`registerTableRows: ${JSON.stringify(ret)}`)
      return ret
    }
  },
  methods: {
    toggleCollapse (namePart) {
      const currentState = this.collapsedRegisters[namePart]
      if (currentState === undefined) {
        this.collapsedRegisters[namePart] = {
          should: false
        }
      }

      const current = this.collapsedRegisters[namePart].should
      this.collapsedRegisters[namePart].should = !current
      this.collapsedRegisters = Object.assign({}, this.collapsedRegisters)
      console.log(`toggle on: ${namePart} -- ${JSON.stringify(this.collapsedRegisters)}`)
    }
  }
}
</script>

<style scoped>
</style>
