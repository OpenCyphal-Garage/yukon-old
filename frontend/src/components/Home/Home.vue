<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div class="m-3 mt-0">
    <div class="row mb-2">
      <ServerHealth class="mr-2"/>
      <BusInfo />
    </div>
    <div class="row m-1 mb-3">
      <NodeList />
    </div>
  </div>
</template>

<script>
import ServerHealth from './ServerHealth'
import BusInfo from './BusInfo'
import NodeList from './NodeList'

export default {
  name: 'Home',
  components: {
    ServerHealth,
    BusInfo,
    NodeList
  }
}
</script>

<style>

</style>
