<!--
 * Copyright (C) 2019-2020 UAVCAN Development Team <uavcan.org>
 *               2020  dronesolutions.io. All rights reserved.
 * This software is distributed under the terms of the MIT License.
 *
 * @author Theodoros Ntakouris <zarkopafilis@gmail.com>
 * @author Nuno Marques <nuno.marques@dronesolutions.io>
 -->

<template>
  <div class="col-sm-2" style="font-family: 'Roboto';">
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
      if (!this.serverHealth || !this.serverHealth.health) {
        return
      }
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
