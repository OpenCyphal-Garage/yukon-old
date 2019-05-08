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
export default {
  name: 'BusInfo',
  data () {
    return {
      info: {
        resilience: 1,
        name: 'cansocket',
        protocol: 'CanFD'
      },
      error: ''
    }
  },
  computed: {
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
  }
}
</script>

<style>

</style>
