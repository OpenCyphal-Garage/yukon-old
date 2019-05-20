<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div :f="Object.keys(workset).length > 0">
    <div class="row ml-2 fit-border mb-0">
        <h4>Workset</h4>
      </div>
      <div class="ml-2">
        <!-- For each register in the workset -->
        <div class="row m-0 col-12" v-for="reg in Object.keys(workset)" :key="reg">
          <h5 class="ml-1 col-12 text-left">~ {{ reg }}</h5>
          <!-- For node with that register -->
          <div class="col-12 text-left ml-2 pb-2" v-for="id in workset[reg].nodeIds" :key="reg + ':' + id">
            <div style="display: inline-block;">
              <h6 class="ml-2">- {{ nodeMapById[id].name + '  ' + '[' + id + ']'}} -></h6>

              <a @click="removeFromWorkgroup(id, reg)">Remove</a>
            </div>
            <TypeValue :ref="reg" class="ml-4" v-bind:val="valueOf(id, reg)" />
          </div>
        </div>
      </div>
      <div class="row ml-2 fit-border mb-0">
        <h4>Register Edit</h4>
      </div>
      <div class="row m-0 col-12 text-left pb-2" v-if="Object.keys(workset).length > 0">
        <TypeEditForm v-bind:type="firstKeyOf(workset).type"/>

        <button @click="updateRegisters(reg)" class="btn btn-primary">Update {{ reg }}</button>
        <p :if="error !== ''"> {{ error }} </p>
      </div>
      <div class="row ml-2 mb-0">
      </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'RegisterWorkset',
  data () {
    return {
      error: ''
    }
  },
  computed: {
    ...mapState({
      registers: state => state.grv.globalRegisterView,
      workset: state => state.grv.registerWorkset
    }),
    ...mapGetters({
      nodeMap: 'grv/nodeMap',
      nodeMapById: 'grv/nodeMapById'
    })
  },
  methods: {
    updateRegisters (reg) {
      const typeValueComponent = this.$refs[reg][0]
      console.log(typeValueComponent)

      if (typeValueComponent.hasErrors()) {
        this.error = 'Please fix all errors before updating registers'
      }

      const value = typeValueComponent.getValue()
      console.log(value)
    },
    valueOf (nodeId, registerName) {
      const n = this.nodeMapById[nodeId]
      if (n === undefined) {
        return undefined
      }

      return n[registerName]
    },
    firstKeyOf (obj) {
      return obj[Object.keys(obj)[0]]
    },
    removeFromWorkset (nodeId, register) {
      this.$store.dispatch('grv/removeNodeFromWorkset', { id: nodeId, register })
    }
  }
}
</script>

<style>

</style>
