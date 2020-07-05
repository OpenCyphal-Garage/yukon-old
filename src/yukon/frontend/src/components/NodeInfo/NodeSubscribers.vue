<!--
  - Copyright (C) 2020 UAVCAN Development Team <uavcan.org>
  -               2020  dronesolutions.io. All rights reserved.
  - This software is distributed under the terms of the MIT License.
  -
  - @author Nuno Marques <nuno.marques@dronesolutions.io>
 -->

<template>
  <div :class="{'subtle-border' : !loading}" style="font-family: 'Roboto';">
    <div v-if="!loading" class="row fit-border pt-2 ml-3 mb-0">
      <p>Node has {{ subscribers.length }} subscrber</p>
    </div>
    <div class="node-params">
      <div v-if="!loading && subscribers.length > 0" class="table-responsive">
        <table class="table table-striped">
        <thead>
          <th>Port ID</th>
          <th>Type</th>
        </thead>

        <tbody ref="nodeListParamsTableBody">
          <tr v-for="sub in subscribers" :key="sub.port_id">
            <td>{{ sub.port_id }}</td>
            <td>{{ sub.type }}</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
    <!-- /Subscriber Data -->

    <div
      v-if="loading && error.length != 0"
      class="row d-flex flex-row justify-content-center fit-border"
    >
      <Spinner></Spinner>
    </div>

    <div v-if="error!==''" class="row d-flex flex-row fit-border mt-2">
      <p class="text-center" style="color: red;">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ApiRoutes from '@/api/ApiRoutes'
import Spinner from '@/components/Util/Spinner'

export default {
  name: 'NodeSubscribers',
  props: ['nodeId'],
  components: {
    Spinner
  },
  data () {
    return {
      loading: false,
      error: '',
      subscribers: []
    }
  },
  async mounted () {
    await this.refreshData()
  },
  methods: {
    async refreshData () {
      this.error = ''
      this.loading = true

      try {
        const response = await axios.get(ApiRoutes.Nodes.GetSubscribersById(this.nodeId))
        const sub = response.data
        this.subscribers = sub
      } catch (e) {
        this.error = e
      }

      this.loading = false
    }
  }
}
</script>

<style scoped>
tr:hover {
  cursor: pointer;
  text-decoration: underline;
}
</style>
