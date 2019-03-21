<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div>
      <div class="row">
        <h2 class="pull-left ml-3">Node Info</h2>
      </div>
      <NodeConstants v-bind:nodeId="_nodeId"></NodeConstants>

      <div class="row">
        <h2 class="pull-left ml-3">Controls</h2>
      </div>
      <NodeControls v-bind:nodeId="_nodeId"></NodeControls>

      <div class="row">
        <h2 class="pull-left ml-3">Configuration Parameters</h2>
      </div>
      <NodeConfigParams v-bind:nodeId="_nodeId"></NodeConfigParams>
  </div>
</template>

<script>
import NodeConstants from './NodeConstants'
import NodeControls from './NodeControls'
import NodeConfigParams from './NodeConfigParams'

export default {
  name: 'NodeInfoPage',
  components: {
    NodeConstants,
    NodeControls,
    NodeConfigParams
  },
  props: ['nodeId'],
  data () {
    return {}
  },
  computed: {
    _nodeId () {
      if (this.nodeId === undefined || this.nodeId.trim() === '') {
        return this.$router.params.nodeId
      }
      return this.nodeId
    }
  }
}
</script>

<style>

</style>
