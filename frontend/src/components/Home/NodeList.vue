<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div>
    <!-- Controls -->
    <div class="row align-items-baseline">
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
    <h2 class="row">Online Nodes</h2>

    <div class="row">
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
            <td><CopyableText v-bind:text="node.id"></CopyableText></td>
            <td><CopyableText v-bind:text="node.name"></CopyableText></td>

            <td :class="node.mode.toLowerCase()">{{ node.mode.toUpperCase() }}</td>
            <td :class="node.health.toLowerCase()">{{ node.health.toUpperCase() }}</td>

            <td>{{ node.uptime }}</td>
            <td>{{ node.vendorCode }}</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <div v-if="loading && error.length != 0" class="row justify-content-center">
      <Spinner></Spinner>
    </div>

    <div  class="row">
      <p class="text-center" style="color: red;">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ApiRoutes from '@/api/ApiRoutes'
import AppRoutes from '@/Router'
import Spinner from '@/components/Util/Spinner'
import CopyableText from '@/components/Util/CopyableText'

export default {
  name: 'NodeList',
  components: {
    Spinner,
    CopyableText
  },
  data () {
    return {
      loading: false,
      nodes: [],
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
      }
    }
  },
  computed: {
    processedNodes: function () {
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
            if (b[this.sortAttribute] > a[this.sortAttribute]) { return -1 }
            if (b[this.sortAttribute] < a[this.sortAttribute]) { return 1 }
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
  mounted () {
    this.refreshData()
  },
  methods: {
    clearControls () {
      this.sortAttribute = 'None'
      this.filter = ''
      this.sortWay = this.sortWays.none.name
    },
    async refreshData () {
      this.error = ''
      this.loading = true

      try {
        const response = await axios.get(ApiRoutes.Nodes.PlugAndPlayTable)
        this.nodes = response.data
      } catch (e) {
        this.error = e
      }

      this.loading = false
    },
    viewNodeDetails (nodeId) {
      this.$router.push({
        name: AppRoutes.NodeDetails.name,
        params: { nodeId: nodeId }
      })
    }
  }
}
</script>

<style>

</style>
