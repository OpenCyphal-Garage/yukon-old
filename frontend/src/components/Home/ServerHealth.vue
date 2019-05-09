<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div class="text-left">
    <div v-if="error === ''">
      <span class="badge" :class="heuristicHealthBadgeColor">{{ health.health }}</span>
      <span class="badge badge-info">Uptime: {{ health.uptime }}s</span>
      <span class="badge badge-secondary">Version {{ health.version }}</span>
    </div>
    <div v-else>
      <p style="color: red;"> {{ error }} </p>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'ServerHealth',
  data () {
    return {
      error: ''
    }
  },
  async mounted () {
    try {
      await this.$store.dispatch('general/getServerHealth')
    } catch (e) {
      this.error = e
    }
  },
  computed: {
    ...mapState({
      nodes: state => state.general.serverHealth
    }),
    heuristicHealthBadgeColor: function () {
      const health = this.health.health.toLowerCase()

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
  }
}
</script>

<style>

</style>
