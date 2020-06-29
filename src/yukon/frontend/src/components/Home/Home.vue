<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
<div :style="{ backgroundImage: 'url(\'' + require('@/assets/wingcopter_model.jpg') + '\')' }">
  <div class="row">
    <div class="col-sm-6">
      <ServerHealth />
      <BusInfo />
    </div>
    <div class="col-sm-6">
      <PlugAndPlayTable />
    </div>
  </div>
  <div class="row m-1 mb-2">
    <div class="col-sm-12">
      <NodeList />
    </div>
    <!-- <div class="col-sm-4">
      <img src="../../assets/wingcopter_model.jpg" alt="Home" width="330%" text-align="center">
    </div> -->
  </div>
</div>

</template>

<script>
import ServerHealth from './ServerHealth'
import BusInfo from './BusInfo'
import NodeList from './NodeList'
import PlugAndPlayTable from './PlugAndPlayTable'

export default {
  name: 'Home',
  components: {
    ServerHealth,
    BusInfo,
    NodeList,
    PlugAndPlayTable // eslint-disable-line vue/no-unused-components
  }
}
</script>

<style>

</style>
