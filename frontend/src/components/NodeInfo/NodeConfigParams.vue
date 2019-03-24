<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div :class="{'subtle-border' : !loading}">
    <div v-if="!loading" class="row fit-border pt-2 ml-3 mb-0">
      <p>Server responded with {{ params.length }} params</p>
    </div>
    <div class="node-params">
      <div v-if="!loading && params.length > 0" class="table-responsive">
        <table class="table table-striped">
        <thead>
          <th>index</th>
          <th>name</th>
          <th>type</th>
          <th>value</th>
          <th>default</th>
          <th>min</th>
          <th>max</th>
        </thead>

        <tbody ref="nodeListParamsTableBody">
          <tr v-for="(param, index) in params" :key="param.name" @click="editParam(param)">
            <td>{{ index }}</td>
            <td>{{ param.name }}</td>
            <td>{{ param.type }}</td>
            <td>{{ param.value }}</td>
            <td>{{ param.default }}</td>
            <!-- Optional -->
            <td>{{ param.min }}</td>
            <td>{{ param.max }}</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
    <!-- /Parameter Data -->

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
import ApiRoutes from '../../api/ApiRoutes'
import Spinner from '../Spinner'

export default {
  name: 'NodeConfigParams',
  props: ['nodeId'],
  components: {
    Spinner
  },
  data () {
    return {
      loading: false,
      error: '',
      params: [{
        name: 'nmea.uart_on',
        type: 'boolean',
        value: 'false',
        default: 'false'
      },
      {
        name: 'uavcan.pubp.pres',
        type: 'integer',
        value: 1,
        default: 0,
        min: 0,
        max: 10000
      },
      {
        name: 'pres.variance',
        type: 'real',
        value: 100.5,
        default: 100.0,
        min: 1.0,
        max: 4000.59
      },
      {
        name: 'advertise.as',
        type: 'string',
        value: 'bestnodeinthebus',
        default: 'simplenode'
      }]
    }
  },
  mounted () {
    this.refreshData()
  },
  methods: {
    async refreshData () {
      this.error = ''
      this.loading = true

      try {
        const response = await axios.get(
          ApiRoutes.Nodes.GetParametersById(this.nodeId)
        )
        this.nodeInfo = response.data
      } catch (e) {
        this.error = e
      }

      this.loading = false
    }
  },
  editParam (param) {
    console.log(JSON.stringify(param)) // stub, todo
  }
}
</script>

<style scoped>
</style>
