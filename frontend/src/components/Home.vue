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
      <h2 class="pull-left">Nodes List</h2>

      <div v-if="!loading" class="list-group-item list-group-item-action flex-column align-items-start clickable mb-1">
        <div v-for="(node) in processedNodes" :key="node.id">
          <div class="d-flex w-100 justify-content-between">
            <div>
              <h3 style="display: inline-block;" class="mr-3 copyable" @click="copyToClipboard(node.name)"
                title="Click to copy">{{ node.name }}</h3>
              <h3 style="display: inline-block;" class="copyable" @click="copyToClipboard(node.id)"
                title="Click to copy">{{ node.id }}</h3>
            </div>

            <div>
              <h5 :class="node.status.toLowerCase()">Status: {{ node.status.toUpperCase() }}</h5>
            </div>
          </div>

          <div class="d-flex w-100 justify-content-between">
            <h6>
              Vendor Code: {{ node.vendorCode }}
            </h6>

            <div>
              <p>Uptime: {{ node.uptime }} s</p>
            </div>
          </div>
        </div>
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
// import axios from 'axios'
// import ApiRoutes from '../api/ApiRoutes'

export default {
  name: 'Home',
  data () {
    return {
      msg: 'Welcome to Yukon',
      loading: false,
      nodes: [
        {
          name: 'node_0',
          id: '9999',
          status: 'UP',
          uptime: 200,
          vendorCode: '000'
        },
        {
          name: 'node_1',
          id: '1000',
          status: 'UP',
          uptime: 500,
          vendorCode: '020'
        },
        {
          name: 'xxx_2',
          id: '5',
          status: 'UP',
          uptime: 20,
          vendorCode: '990'
        }
      ],
      error: '',
      filter: '',
      sortAttribute: 'None',
      sortWay: 'None',
      sortAttributes: ['None', 'name', 'id', 'uptime', 'vendorCode'],
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
      }
    }
  },
  computed: {
    processedNodes: function () {
      let filtered = this.nodes

      if (this.filter && this.filter !== '') {
        console.log('Filtering on: ' + this.filter)
        filtered = filtered.filter(x => x.name.includes(this.filter) || x.name.match(this.filter))
        filtered.sort((a, b) => a.name.indexOf(this.filter) - b.name.indexOf(this.filter))
      }

      if (this.sortAttribute !== 'None') {
        // eslint-disable-next-line
        filtered.sort((a, b) => { b[this.sortAttribute] > a[this.sortAttribute] ? -1 : (b[this.sortAttribute] < a[this.sortAttribute] ? 1 : 0) })

        if (this.sortWay === this.sortWays.ascending.name) {
          filtered.reverse()
        }
      }

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
      // this.error = ''
      // this.loading = true

      // axios
      //   .get(ApiRoutes.Nodes.GetAll)
      //   .then(response => {
      //     this.nodes = response.data
      //     this.loading = false
      //   })
      //   .catch(e => {
      //     this.error = e
      //     this.loading = false
      //   })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
.up {
  color: green;
}

.copyable:hover {
  text-decoration: underline;
  cursor: pointer;
  z-index: 2;
}

.clickable:hover {
  cursor: pointer;
}
</style>
