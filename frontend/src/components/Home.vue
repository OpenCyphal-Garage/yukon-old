<template>
  <div>
    <!-- Controls -->
    <div class="row">
      <h2 class="pull-left">Filters</h2>
    </div>

    <div class="row align-items-baseline">
      <div class="btn-group col-3 pl-0 mr-2 align-items-baseline">
        <input v-model="filter" class="form-control" type="text" placeholder="Filter" aria-label="Search">
      </div>

      <div class="form-group mr-2">
        <label for="sortAttribute">Sort On:</label>

        <select v-model="sortAttribute" id="sortAttribute">
          <option v-for="s in sortAttributes" :key="s">{{ s }}</option>
        </select>
      </div>

      <div class="form-group mr-4">
        <label for="sortWay"> With Order: </label>

        <select v-model="sortWay" id="sortWay">
          <option v-for="s in sortWays" :key="s.name">{{ s.name }}</option>
        </select>
      </div>

      <button type="button" class="btn btn-secondary" @click="clearControls()">Clear</button>
    </div>

    <!-- Nodes List -->
    <div class="row">
      <h2 class="pull-left">Online Nodes List</h2>

      <div v-if="!loading" class="table table-striped">
        <thead>
          <th>id</th>
          <th>name</th>
          <th>mode</th>
          <th>health</th>
          <th>uptime</th>
          <th>vendor</th>
        </thead>

        <tbody>
          <tr v-for="(node) in processedNodes" :key="node.id">
            <td class="copyable" @click="copyToClipboard(node.id)"
                title="Click to copy">{{ node.id }}</td>
            <td class="copyable col" @click="copyToClipboard(node.name)"
                title="Click to copy">{{ node.name }}</td>

            <td :class="node.mode.toLowerCase()">{{ node.mode.toUpperCase() }}</td>
            <td :class="node.health.toLowerCase()">{{ node.health.toUpperCase() }}</td>

            <td>{{ node.uptime }}</td>
            <td>{{ node.vendorCode }}</td>
          </tr>
        </tbody>
      </div>
    </div>

    <div v-if="loading && nodes.length == 0" class="row">
      <p class="text-center">Loading...</p>
    </div>

    <div v-if="!loading && error.length != 0" class="row">
      <p class="text-center" style="color: red;">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ApiRoutes from '../api/ApiRoutes'

export default {
  name: 'Home',
  data () {
    return {
      msg: 'Welcome to Yukon',
      loading: false,
      nodes: [
        {
          name: 'bnode_0',
          id: '9999',
          health: 'OK',
          mode: 'OPERATIONAL',
          uptime: 200,
          vendorCode: '000'
        },
        {
          name: 'anode_1',
          id: '1000',
          health: 'WARNING',
          mode: 'INITIALISATION',
          uptime: 500,
          vendorCode: '020'
        },
        {
          name: 'xxx_2',
          id: '5',
          health: 'ERROR',
          mode: 'MAINTAINANCE',
          uptime: 20,
          vendorCode: '990'
        },
        {
          name: 'zzz_3',
          id: '6',
          health: 'CRITICAL',
          mode: 'SOFTWARE_UPDATE',
          uptime: 20,
          vendorCode: '990'
        },
        {
          name: 'aa_4',
          id: '7',
          health: 'OK',
          mode: 'OFFLINE',
          uptime: 20,
          vendorCode: '990'
        }
      ],
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
        INITIALISATION: 1,
        MAINTAINANCE: 2,
        SOFTWARE_UPDATE: 3,
        OFFLINE: 4
      }
    }
  },
  computed: {
    processedNodes: function () {
      let filtered = this.nodes

      if (this.filter && this.filter !== '') {
        console.log('Filtering on: ' + this.filter)

        filtered = filtered.filter(x =>
          x.name.includes(this.filter) || x.name.match(this.filter) ||
          x.health.includes(this.filter) || x.mode.includes(this.filter))
        filtered.sort((a, b) => a.name.indexOf(this.filter) - b.name.indexOf(this.filter))
      }

      if (this.sortAttribute !== 'None' && this.sortAttribute !== 'health' && this.sortAttribute !== 'mode') {
        if (['id', 'uptime'].includes(this.sortAttribute)) {
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

      console.log(JSON.stringify(filtered))
      return filtered
    }
  },
  mounted () {
    this.refreshData()
  },
  methods: {
    copyToClipboard (text) {
      const el = document.createElement('textarea')
      el.value = text
      el.setAttribute('readonly', '')
      el.style = {position: 'absolute', left: '-9999px'}
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
    },
    clearControls () {
      this.sortAttribute = 'None'
      this.filter = ''
      this.sortWay = this.sortWays.none.name
    },
    refreshData () {
      this.error = ''
      this.loading = true

      axios
        .get(ApiRoutes.Nodes.GetAll)
        .then(response => {
          this.nodes = response.data
          this.loading = false
        })
        .catch(e => {
          this.error = e
          this.loading = false
        })
    }
  }
}
</script>

<style scoped>
  @import '../assets/styles/nodeStatus.css';
</style>
