<!--
 * Copyright (C) 2019-2020 UAVCAN Development Team <uavcan.org>
 *               2020  dronesolutions.io. All rights reserved.
 * This software is distributed under the terms of the MIT License.
 *
 * @author Theodoros Ntakouris <zarkopafilis@gmail.com>
 * @author Nuno Marques <nuno.marques@dronesolutions.io>
 -->

<template>
<div :style="{ backgroundImage: 'url(\'' + require('@/assets/wingcopter_model.jpg') + '\')' }">
  <div class="row">
    <ServerHealth />
    <BusInfo />
  </div>
  <div class="row">
    <div class="col-sm-6">
      <PlugAndPlayTable />
    </div>
  </div>
  <div class="row m-1 mb-2">
    <div class="col-sm-12">
      <NodeList />
    </div>
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
    PlugAndPlayTable
  }
}
</script>

<style>

</style>
