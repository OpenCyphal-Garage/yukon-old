<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div class="subtle-border">
    <div class="fit-border">
      <div class="row d-flex flex-row">
        <button type="button" @click="shutdownNode" class="btn btn-danger mr-2" ref="shutdownButton">Shutdown</button>
        <button type="button" @click="startFirmwareUpdate" class="btn btn-warning" ref="startFirmwareUpdateButton">Start firmware update</button>
      </div>

      <div v-if="text!==''" class="row d-flex flex-row fit-border">
        <p class="text-center">{{ text }}</p>
      </div>

      <div v-if="error!==''" class="row d-flex flex-row fit-border">
        <p class="text-center" style="color: red;">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ApiRoutes from '../../api/ApiRoutes'

export default {
  name: 'NodeControls',
  props: ['nodeId'],
  data () {
    return {
      text: '',
      error: ''
    }
  },
  methods: {
    async startFirmwareUpdate () {
      try {
        const response = await axios.post(ApiRoutes.Nodes.StartFirmwareUpdateById(this.nodeId))
        if (response.status === 200) {
          this.text = 'Sucessfully started firmware update'
        }
      } catch (e) {
        this.error = `Firmware update start failed: ${e}`
      }
    },
    async shutdownNode () {
      try {
        const response = await axios.post(ApiRoutes.Nodes.ShutdownById(this.nodeId))
        if (response.status === 200) {
          this.text = 'Sucessfully started node shutdown'
        }
      } catch (e) {
        this.error = `Node shutdown failed: ${e}`
      }
    }
  }
}
</script>

<style>

</style>
