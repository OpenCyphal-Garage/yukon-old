<template>
  <div>
    <!-- Controls -->
    <div class="row">
      <h2 class="pull-left">Nodes List</h2>

      <div v-if="!loading" class="list-group-item list-group-item-action flex-column align-items-start">
        <div v-for="(node) in nodes" :key="node.id">
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
        }
      ],
      error: ''
    }
  },
  mounted () {
    // axios
    //   .get(ApiRoutes.Nodes.GetAll)
    //   .then(response => (this.nodes = response.data))
    //   .catch(error => console.log(error))
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
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.up {
  color: green;
}

.copyable:hover {
  text-decoration: underline;
  cursor: pointer;
  z-index: 2;
}
</style>
