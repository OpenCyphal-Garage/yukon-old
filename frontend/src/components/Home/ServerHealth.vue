<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div class="text-left">
    <div v-if="error === ''">
      <span class="badge" :class="heuristicHealthBadgeColor">{{ serverHealth.health }}</span>
      <span class="badge badge-info">Uptime: {{ serverHealth.uptime }}s</span>
      <span class="badge badge-secondary">Version {{ serverHealth.version }}</span>
    </div>
    <div v-else>
      <p style="color: red;"> {{ error }} </p>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'ServerHealth',
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
      serverHealth: state => state.general.serverHealth
    }),
    heuristicHealthBadgeColor: function () {
      const health = this.serverHealth.health.toLowerCase()

      if (health.includes('good') ||
      health.includes('running') ||
      health.includes('operational') ||
      health.includes('initial')) {
        return 'badge-success'
      }

      if (health.includes('warning')) {
        return 'badge-warning'
      }

      if (health.includes('error') ||
      health.includes('not found') ||
      health.includes('critical')) {
        return 'badge-danger'
      }

      return 'badge-light'
    }
  },
  methods: {
    async loadData () {
      this.error = ''
      try {
        await this.$store.dispatch('general/getServerHealth')
      } catch (e) {
        this.error = e
      }
    }
  }
}
</script>

<style>

</style>
