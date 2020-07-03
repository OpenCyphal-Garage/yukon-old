<!--
 * Copyright (C) 2020 UAVCAN Development Team <uavcan.org>
 *               2020  dronesolutions.io. All rights reserved.
 * This software is distributed under the terms of the MIT License.
 *
 * @author Nuno Marques <nuno.marques@dronesolutions.io>
 -->

<template>
  <div :class="{'subtle-border' : !loading}">
    <div v-if="!loading" class="row fit-border pt-2 ml-3 mb-0">
      <p>Node has {{ publishers.length }} publisher</p>
    </div>
    <div class="node-params">
      <div v-if="!loading && publishers.length > 0" class="table-responsive">
        <table class="table table-striped">
        <thead>
          <th>Port ID</th>
          <th>Type</th>
          <th>Current rate</th>
        </thead>

        <tbody ref="nodeListParamsTableBody">
          <tr v-for="(pub, index) in publishers" :key="port_id">
            <td>{{ pub.port_id }}</td>
            <td>{{ pub.type }}</td>
            <td>{{ pub.rate }} Hz</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
    <!-- /Publisher Data -->

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
  name: 'NodePublishers',
  props: ['nodeId'],
  components: {
    Spinner
  },
  data () {
    return {
      loading: false,
      error: '',
      publishers: []
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
        const response = await axios.get(ApiRoutes.Nodes.GetPublishersById(this.nodeId))
        const pub = response.data
        this.publishers = pub
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
