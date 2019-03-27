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
          <th> register </th>
          <th v-for="node in nodeMap" :key="node.name">
            {{ node.name }}
          </th>
        </thead>

        <tbody>
          <tr v-for="row in paramRows" :key="row.key">
            <td >{{ row.name }}</td>
            <td v-for="(d, index) in row.data" :key="index"> {{ d }}</td>
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
      params: [
        {
          nodeId: 0,
          nodeName: 'esc0',
          paramName: 'uavcan.a.b',
          value: 'asdf'
        },
        {
          nodeId: 1,
          nodeName: 'esc1',
          paramName: 'uavcan.a.b',
          value: 'ghjk'
        },
        {
          nodeId: 2,
          nodeName: 'esc2',
          paramName: 'uavcan.a.b',
          value: 'qwer'
        },
        {
          nodeId: 3,
          nodeName: 'esc3',
          paramName: 'uavcan.a.b',
          value: 'tyui'
        },
        {
          nodeId: 0,
          nodeName: 'esc0',
          paramName: 'uavcan.a.something',
          value: 0
        },
        {
          nodeId: 4,
          nodeName: 'gps',
          paramName: 'uavcan.gps.a',
          value: 1
        },
        {
          nodeId: 4,
          nodeName: 'gps',
          paramName: 'uavcan.gps.b',
          value: 2
        }]
    }
  },
  computed: {
    nodeMap: function () {
      let nodes = {}

      this.params.forEach(element => {
        if (nodes[element.nodeName] === undefined) {
          nodes[element.nodeName] = {
            name: element.nodeName
          }
        }

        nodes[element.nodeName][element.paramName] = {
          value: element.value
        }
      })

      return nodes
    },
    paramRows: function () {
      const self = this
      let tree = {}
      // construct parameter tree
      this.params.forEach(element => {
        const paramNameParts = element.paramName.split('.')
        const paramNameTreeBranches = paramNameParts.slice(0, -1)

        let pos = tree
        paramNameTreeBranches.forEach(param => {
          if (pos[param] === undefined) {
            pos[param] = {}
          }

          pos = pos[param]
        })

        pos[paramNameParts.slice(-1)[0]] = element.paramName
      })

      let rows = []
      let row = -1
      const numberOfNodes = Object.keys(this.nodeMap).length
      console.log('\n\n\n DATA APPEND:')

      function appendData (t, indent) {
        row++
        for (const [_n, value] of Object.entries(t)) {
          rows[row] = {
            name: _n,
            key: row + _n,
            indent: indent,
            data: new Array(numberOfNodes)
          }

          if (typeof value === 'object') {
            console.log(`branch (${row}): ${_n}`)
            appendData(value, indent + 1)
          } else {
            console.log(`leaf (${row}): ${_n}`)
            let i = 0

            for (const [_, node] of Object.entries(self.nodeMap)) { // eslint-disable-line no-unused-vars
              const x = node[value]
              if (x !== undefined) {
                rows[row].data[i++] = x.value === undefined && x.value != null ? '' : x.value
              } else {
                i++ // empty column // padding (for leaf nodes only)
              }
            }

            row++
          }
        }
      }
      appendData(tree, 0)
      console.log('\n\n\n ROWS:')
      rows.forEach(element => {
        console.log(`${element.name} - ${JSON.stringify(element.data)}`)
      })
      return rows
    }
  }
}
</script>

<style scoped>
</style>
