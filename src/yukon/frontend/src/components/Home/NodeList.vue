<!--
 * Copyright (C) 2019-2020 UAVCAN Development Team <uavcan.org>
 *               2020  dronesolutions.io. All rights reserved.
 * This software is distributed under the terms of the MIT License.
 *
 * @author Theodoros Ntakouris <zarkopafilis@gmail.com>
 * @author Nuno Marques <nuno.marques@dronesolutions.io>
 -->

<template>
<div>
  <!-- Controls -->
  <div class="row align-items-baseline" style="display: none;">
    <div class="btn-group col-3 pl-0 mr-2 align-items-baseline">
      <input v-model="filter" ref="textFilter" class="form-control" type="text" placeholder="Filter" aria-label="Search">
    </div>

    <div class="form-group mr-2">
      <label for="sortAttribute">Sort on:</label>

      <select v-model="sortAttribute" ref="sortAttribute">
        <option v-for="s in sortAttributes" :key="s">{{ s }}</option>
      </select>
    </div>

    <div class="form-group mr-4">
      <label for="sortWay"> With order: </label>

      <select v-model="sortWay" ref="sortWay">
        <option v-for="s in sortWays" :key="s.name">{{ s.name }}</option>
      </select>
    </div>

    <button type="button" class="btn btn-secondary" @click="clearControls()">Clear</button>
  </div>

  <!-- Nodes List -->
  <h2 style="text-align: center; font-family: 'Russo One';">Online Nodes</h2>

  <div class="row" style="display: none;">
    <p v-if="error == '' && !loading && processedNodes.length == 0">No nodes found</p>

    <div v-if="!loading && processedNodes.length > 0" class="table-responsive">
      <table class="table table-striped">
        <thead>
          <th>id</th>
          <th>name</th>
          <th>mode</th>
          <th>health</th>
          <th>uptime</th>
          <th>vendor</th>
        </thead>

        <tbody ref="nodeListTableBody">
          <tr v-for="(node) in processedNodes" :key="node.id" @click="viewNodeDetails(node.id)">
            <td>
              <CopyableText v-bind:text="node.id"></CopyableText>
            </td>
            <td>
              <CopyableText v-bind:text="node.name"></CopyableText>
            </td>

            <td :class="node.mode.toLowerCase()">{{ node.mode.toUpperCase() }}</td>
            <td :class="node.health.toLowerCase()">{{ node.health.toUpperCase() }}</td>

            <td>{{ node.uptime }}</td>
            <td>{{ node.vendorCode }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="row">
    <p v-if="error == '' && !loading && processedNodes.length == 0">No nodes found</p>

    <div v-if="!loading && processedNodes.length > 0">
      <v-stage ref="stage" :config="configKonva">
        <v-layer ref="layer">
          <v-group v-for="(node) in this.nodes" :key="node.id" @click="viewNodeDetails(node.id)" :config="{
                x: 100,
                y: 100,
                id: node.id,
                draggable: true
         }">
            <v-rect :config="{
                        width: 300,
                        height: 100,
                        opacity: 0.6,
                        fill: 'white',
                        stroke: 'black',
                        shadowBlur: 10,
                        shadowColor: 'black',
                        shadowOpacity: 0.6,
                }"></v-rect>
            <v-text :config="{
                        x: 10,
                        y: 10,
                        fontSize: 16,
                        fontFamily: 'Russo One',
                        text: 'Node ID ' + node.id,
                }"></v-text>
            <v-text :config="{
                        x:140,
                        y:10,
                        fontSize: 16,
                        fontFamily: 'Russo One',
                        text: node.name,
                }"></v-text>
            <v-text :config="{
                        x:10,
                        y:40,
                        fontSize: 16,
                        fontFamily: 'Russo One',
                        text: 'Mode: ' + node.mode,
                }"></v-text>
            <v-text :config="{
                        x:10,
                        y:70,
                        fontSize: 16,
                        fontFamily: 'Russo One',
                        text: 'Health: ' + node.health,
                }"></v-text>
          </v-group>
        </v-layer>
      </v-stage>
    </div>
  </div>

  <div v-if="loading && error.length != 0" class="row justify-content-center">
    <Spinner></Spinner>
  </div>

  <div class="row">
    <p class="text-center" style="color: red;">{{ error }}</p>
  </div>
</div>
</template>

<script>
import {
  mapState
}
from 'vuex'
import AppRoutes from '@/Router'
import Spinner from '@/components/Util/Spinner'
import CopyableText from '@/components/Util/CopyableText'

const width = window.innerWidth
const height = window.innerHeight

export default {
  name: 'NodeList',
  components: {
    Spinner,
    CopyableText
  },
  data() {
    return {
      loading: false,
      error: '',
      filter: '',
      sortAttribute: 'None',
      sortWay: 'None',
      sortAttributes: ['None', 'name', 'id', 'uptime', 'vendorCode', 'health', 'mode'],
      sortWays: {
        none: {
          name: 'None'
        },
        ascending: {
          name: 'ascending'
        },
        descending: {
          name: 'descending'
        }
      },
      health: {
        OK: 0,
        WARNING: 1,
        ERROR: 2,
        CRITICAL: 3
      },
      mode: {
        OPERATIONAL: 0,
        INITIALIZATION: 1,
        MAINTAINANCE: 2,
        SOFTWARE_UPDATE: 3,
        OFFLINE: 4
      },
      list: [],
      dragItemId: null,
      configKonva: {
        width: width,
        height: height
      }
    }
  },
  computed: {
    ...mapState({
      nodes: state => state.nodes.nodeList
    }),
    processedNodes: function() {
      let filtered = this.nodes
      const lowerFilter = this.filter.toLowerCase()

      if (this.filter && this.filter !== '') {
        filtered = filtered.filter(x =>
          x.name.toLowerCase().includes(lowerFilter) || x.name.match(this.filter) || (x.id + '').match(this.filter) ||
          x.health.toLowerCase().includes(lowerFilter) || x.mode.toLowerCase().includes(lowerFilter))
        filtered.sort((a, b) => a.name.indexOf(this.filter) - b.name.indexOf(this.filter))
      }

      if (this.sortAttribute !== 'None' && this.sortAttribute !== 'health' && this.sortAttribute !== 'mode') {
        if (['id', 'uptime', 'vendorCode'].includes(this.sortAttribute)) {
          filtered.sort((a, b) => a[this.sortAttribute] - b[this.sortAttribute])
        } else {
          // eslint-disable-next-line
          filtered.sort((a, b) => {
            if (b[this.sortAttribute] > a[this.sortAttribute]) {
              return -1
            }
            if (b[this.sortAttribute] < a[this.sortAttribute]) {
              return 1
            }
            return 0
          })
        }

        if (this.sortWay === this.sortWays.ascending.name) {
          filtered.reverse()
        }
      } else {
        if (this.sortAttribute === 'health') {
          filtered.sort((a, b) => this.health[a.health] - this.health[b.health])
        } else if (this.sortAttribute === 'mode') {
          filtered.sort((a, b) => this.mode[a.mode] - this.mode[b.mode])
        }
      }

      return filtered
    }
  },
  async mounted() {
    await this.loadData()
    // for (let n = 0; n < 6; n++) {
    //   this.list.push({
    //     id: Math.round(Math.random() * 10000).toString(),
    //     x: Math.random() * width,
    //     y: Math.random() * height
    //   })
    // }
  },
  methods: {
    clearControls() {
      this.sortAttribute = 'None'
      this.filter = ''
      this.sortWay = this.sortWays.none.name
    },
    async loadData() {
      this.error = ''
      this.loading = true
      try {
        await this.$store.dispatch('nodes/getNodeList')
      } catch (e) {
        this.error = e
      }
      this.loading = false
    },
    viewNodeDetails(nodeId) {
      this.$router.push({
        name: AppRoutes.NodeDetails.name,
        params: {
          nodeId: nodeId
        }
      })
    }
  }
}
</script>
