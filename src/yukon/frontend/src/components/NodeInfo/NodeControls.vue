<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div class="subtle-border" style="font-family: Roboto, Monospace;">
    <div class="fit-border">
      <div class="row d-flex flex-row">
        <button type="button" @click="showRestartConfirmationDialog()" class="btn btn-danger mr-2" ref="restartButton">Restart</button>
        <button type="button" @click="openFileSelect()" class="btn btn-warning" ref="startFirmwareUpdateButton">Start firmware update</button>

        <input ref="fileInput" style="display: none;" type="file" v-on:change="fileSelected"/>
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
import ApiRoutes from '@/api/ApiRoutes'

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
    openFileSelect () {
      this.$refs.fileInput.click()
    },
    async fileSelected (ev) {
      const file = ev.target.files[0]
      const reader = new FileReader()

      const contents = reader.readAsText(file)

      await this.startFirmwareUpdate(contents)
    },
    async showRestartConfirmationDialog () {
      const result = confirm(`Are you sure you want to restart node ${this.nodeId}? This operation is non-revertible.`)

      if (result) {
        await this.restartNode()
      }
    },
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
    async restartNode () {
      try {
        const response = await axios.post(ApiRoutes.Nodes.RestartById(this.nodeId))
        if (response.status === 200) {
          this.text = 'Sucessfully started node restart operation'
        }
      } catch (e) {
        this.error = `Node restart failed: ${e}`
      }
    }
  }
}
</script>

<style>

</style>
