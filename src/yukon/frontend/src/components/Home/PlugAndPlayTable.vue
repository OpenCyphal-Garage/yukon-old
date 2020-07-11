<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div class="mt-0" style="font-family: Roboto, Monospace; display: none;">
    <div v-if="error === ''">
      <input v-model="search" ref="textSerarch" class="form-control col-sm-3" type="text"
       placeholder="Search PnP Table" aria-label="Search">

      <table id="plugAndPlayTable" ref="plugAndPlayTable"
       class="table table-striped table-sm table-borderless" summary="Plug-and-Play table">
        <thead>
          <tr>
            <th scope="nodeId">Node Id</th>
            <th scope="uniqueId">Unique Id</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(nid, uid) in filteredData" :key="nid">
            <td>{{ nid }}</td>
            <td>{{ uid }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>
      <p style="color: red;"> {{ error }} </p>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'PlugAndPlayTable',
  data () {
    return {
      search: '',
      error: ''
    }
  },
  async mounted () {
    await this.loadData()
  },
  computed: {
    ...mapState({
      data: state => state.nodes.plugAndPlayTable
    }),
    filteredData: function () {
      const search = this.search
      const data = this.data

      if (search === '' || this.error !== '') {
        return data
      }

      return Object.keys(data)
        .filter(nid => ('' + nid).includes(search) ||
        ('' + data[nid]).includes(search))
        .reduce((obj, key) => {
          return {
            ...obj,
            [key]: data[key]
          }
        }, {})
    }
  },
  methods: {
    async loadData () {
      this.error = ''
      try {
        await this.$store.dispatch('nodes/getPlugAndPlayTable')
      } catch (e) {
        this.error = e
      }
    }
  }
}
</script>

<style>

</style>
