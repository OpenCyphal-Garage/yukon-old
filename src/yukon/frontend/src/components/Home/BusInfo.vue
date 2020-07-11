<!--
 * Copyright (C) 2019-2020 UAVCAN Development Team <uavcan.org>
 *               2020  dronesolutions.io. All rights reserved.
 * This software is distributed under the terms of the MIT License.
 *
 * @author Theodoros Ntakouris <zarkopafilis@gmail.com>
 * @author Nuno Marques <nuno.marques@dronesolutions.io>
 -->

<template>
<div class="col-sm-3" style="font-family: Roboto, Monospace;">
  <div v-if="error === ''">
    <div class="row">
      <div class="col-sm-3">
        <span class="badge" :class="resilienceColor">Resilience: {{ info.resilience }}</span>
      </div>
      <div class="col-sm-8">
        <p style="vertical-align: right;">Bus: {{ info.name }} running on {{ info.transport }}</p>
      </div>
    </div>
  </div>
  <div v-else>
    <p style="color: red;"> {{ error }} </p>
  </div>
</div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'BusInfo',
  data () {
    return {
      error: ''
    }
  },
  async mounted () {
    await this.loadData()
  },
  computed: {
    ...mapState({
      info: state => state.general.busInfo
    }),
    resilienceColor: function () {
      const res = this.info.resilience

      if (res >= 3) {
        return 'badge-success'
      }

      if (res === 1) {
        return 'badge-warning'
      }

      if (res === 2) {
        return 'badge-primary'
      }

      return 'badge-light'
    }
  },
  methods: {
    async loadData () {
      this.error = ''
      try {
        await this.$store.dispatch('general/getBusInfo')
      } catch (e) {
        this.error = e
      }
    }
  }
}
</script>

<style>

</style>
