<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div :class="{'subtle-border' : !loading}" style="font-family: Roboto, Monospace;">
    <div v-if="!loading" class="row fit-border pt-2 ml-3 mb-0">
      <p>Server responded with {{ registers.length }} registers</p>
    </div>
    <div class="node-params">
      <div v-if="!loading && registers.length > 0" class="table-responsive">
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
          <tr v-for="(reg, index) in registers" :key="reg.name" @click="editRegister(reg)">
            <td>{{ index }}</td>
            <td>{{ reg.name }}</td>
            <td>{{ reg.type }}</td>
            <td>{{ reg.value }}</td>
            <td>{{ reg.default }}</td>
            <!-- Optional -->
            <td>{{ reg.min }}</td>
            <td>{{ reg.max }}</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
    <!-- /Register Data -->

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
  name: 'NodeRegisters',
  props: ['nodeId'],
  components: {
    Spinner
  },
  data () {
    return {
      loading: false,
      error: '',
      registers: [],
      targetRegister: ''
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
        const response = await axios.get(ApiRoutes.Nodes.GetRegistersById(this.nodeId))
        const reg = response.data
        this.registers = reg
      } catch (e) {
        this.error = e
      }

      this.loading = false
    }
  },
  editRegister (register) {
    this.targetRegister = register
    this.$refs.modal.modal()
  }
}
</script>

<style scoped>
tr:hover {
  cursor: pointer;
  text-decoration: underline;
}
</style>
