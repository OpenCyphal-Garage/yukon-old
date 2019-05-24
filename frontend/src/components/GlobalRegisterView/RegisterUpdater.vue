<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div>
    <div class="row m-0 col-12 text-left pb-2">
      <TypeEditForm ref="form" :type="type"/>
    </div>

    <div v-if="!loading" class="ml-4 mb-2">
      <div class="row">
        <div class="col-4">
          <button @click="tryUpdateRegister()" class="btn btn-primary">{{ registerUpdateFailed ? 'Retry updating' : 'Update' }} {{ register }}</button>

        </div>
        <div :if="registerUpdateFailed" class="col-8">
            <div v-for="failedNode in failedNodes" :key="failedNode.id">
              <input v-model="failedNode.selected" type="checkbox">
              <label style="display: inline-block;">{{`${failedNode.id} => ${failedNode.error}`}}</label>
            </div>
        </div>
      </div>

      <div class="row ml-0 mt-1">
        <p class="small">Changes will affect node ids: [{{ this.targetNodes.join(', ') }}]</p>
      </div>
      <div class="row m-0 p-0" v-if="registerUpdateFailed">
        <p style="color: red;"> Register update unsuccessful</p>
      </div>
      <div class="row m-0 p-0">
        <p style="color: red;" :if="error !== ''"> {{ error }} </p> <!-- User Input Validation Error -->
      </div>
    </div>
    <div v-else class="row ml-4 mb-2">
      <p class="ml-1" style="color: blue;"> Updating Registers... </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ApiRoutes from '@/api/ApiRoutes'
import TypeEditForm from '@/components/Dsdl/TypeEditForm'

export default {
  name: 'RegisterUpdater',
  props: ['register', 'type', 'nodeIds'],
  components: {
    TypeEditForm
  },
  data () {
    return {
      error: '',
      loading: false,
      failedNodes: []
    }
  },
  computed: {
    registerUpdateFailed () {
      return this.failedNodes.length > 0
    },
    targetNodes () {
      const ret = this.registerUpdateFailed ? this.failedNodes.filter(node => node.selected).map(node => node.id)
        : this.nodeIds

      return ret
    }
  },
  methods: {
    async tryUpdateRegister () {
      if (this.targetNodes.length === 0) {
        this.error = 'Please select at least one target node'
        return
      }

      const typeValueComponent = this.$refs.form

      this.error = ''
      if (typeValueComponent.hasError()) {
        this.error = 'Please fix all errors before updating the register'
      }

      const value = typeValueComponent.getValue()
      await this.updateRegister(value)
    },
    async updateRegister (value) {
      this.loading = true
      this.failedNodes = []

      await Promise.all(this.targetNodes.map(async nodeId => {
        try {
          await axios.put(ApiRoutes.Nodes.UpdateRegisterByIdAndName(nodeId, value))
        } catch (e) {
          this.failedNodes.push({ id: nodeId, error: e, selected: true })
        }
      }))

      this.loading = false
    }
  }
}
</script>

<style>

</style>
