<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div>
    <div v-if="error === ''">
      <span class="badge float-left" :class="resilienceColor">Resilience: {{ info.resilience }}</span>
      <p style="vertical-align: middle;">Bus: {{ info.name }} running on {{ info.protocol }}</p>
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
