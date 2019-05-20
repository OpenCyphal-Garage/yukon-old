<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div>
    <div class="row ml-2 fit-border mb-0">
        <h4>Workset</h4>
      </div>
      <div class="ml-2">
        <!-- For each register in the workset -->
        <div class="row m-0 col-12" v-for="reg in Object.keys(workset)" :key="reg">
          <h5 class="ml-1 col-12 text-left">~ {{ reg }}</h5>
          <!-- For node with that register -->
          <div class="col-12 text-left ml-2 pb-2" v-for="id in workset[reg].nodeIds" :key="reg + ':' + id">
            <h6 class="ml-2">- {{ nodeMapById[id].name + '  ' + '[' + id + ']'}} -></h6>
            <TypeValue class="ml-4" v-bind:val="valueOf(id, reg)" />
          </div>
        </div>
      </div>
      <div class="row ml-2 fit-border mb-0">
        <h4>Register Edit</h4>
      </div>
      <div class="row m-0 col-12 text-left pb-2" v-if="Object.keys(workset).length > 0">
        <TypeEditForm v-bind:type="firstKeyOf(workset).type"/>
      </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'RegisterWorkset',
  computed: {
    ...mapState({
      registers: state => state.grv.globalRegisterView
    }),
    ...mapGetters({
      nodeMap: 'grv/nodeMap',
      nodeMapById: 'grv/nodeMapById'
    })
  },
  methods: {
    valueOf (nodeId, registerName) {
      const n = this.nodeMapById[nodeId]
      if (n === undefined) {
        return undefined
      }

      return n[registerName]
    },
    firstKeyOf (obj) {
      return obj[Object.keys(obj)[0]]
    }
  }
}
</script>

<style>

</style>
