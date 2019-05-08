<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div class="row">
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
export default {
  name: 'ServerHealth',
  data () {
    return {
      health: {
        uptime: 1000,
        health: 'Health is good',
        version: '1.2.3'
      },
      error: ''
    }
  },
  computed: {
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
