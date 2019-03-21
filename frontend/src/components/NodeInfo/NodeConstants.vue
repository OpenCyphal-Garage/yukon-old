<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div :class="{'subtle-border' : !loading}">
    <div class="node-constants fit-border">
      <div class="row d-flex flex-row d-flex flex-row d-flex flex-row">
          <p class="mr-2">ID:</p>
          <CopyableText v-bind:text='nodeInfo.id' class="mr-5"></CopyableText>

          <p class="mr-2">Name:</p>
          <CopyableText v-bind:text='nodeInfo.name'></CopyableText>
      </div>

      <div class="row d-flex flex-row">
          <p class="mr-2">Mode:</p>
          <p :class='nodeInfo.mode.toLowerCase()' class="mr-5">{{ nodeInfo.mode }}</p>

          <p class="mr-2">Health:</p>
          <p :class='nodeInfo.health.toLowerCase()' class="mr-5">{{ nodeInfo.health }}</p>

          <p class="mr-2">Uptime:</p>
          <p class="mr-5">{{ nodeInfo.uptime }}</p>
      </div>

      <div class="row d-flex flex-row">
          <p class="mr-2">Vendor Code:</p>
          <CopyableText v-bind:text='nodeInfo.vendorCode' class="mr-5"></CopyableText>
      </div>

      <div class="row d-flex flex-row">
          <p class="mr-2">Software Version:</p>
          <p class="mr-5">{{ nodeInfo.softwareVersion }}</p>

          <p class="mr-2">CRC 64:</p>
          <CopyableText v-bind:text='nodeInfo.crc' class="mr-5"></CopyableText>
      </div>

      <div class="row d-flex flex-row">
          <p class="mr-2">Hardware Version:</p>
          <p class="mr-5">{{ nodeInfo.hardwareVersion }}</p>

          <p class="mr-2">UID:</p>
          <CopyableText v-bind:text='nodeInfo.uid' class="mr-5"></CopyableText>
      </div>

      <div class="row d-flex flex-row">
          <p class="mr-2">Certificate of authenticity:</p>
          <CopyableText v-bind:text='nodeInfo.authenticity' class="mr-5"></CopyableText>
      </div>

    </div>
    <!-- /Data -->

    <div v-if='loading && error.length != 0' class="row d-flex flex-row justify-content-center fit-border">
      <Spinner></Spinner>
    </div>

    <div class="row d-flex flex-row fit-border">
      <p class="text-center" style="color: red;">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ApiRoutes from '../../api/ApiRoutes'
import Spinner from '../Spinner'
import CopyableText from '../CopyableText'

export default {
  name: 'NodeConstants',
  props: ['nodeId'],
  components: {
    CopyableText,
    Spinner
  },
  data () {
    return {
      loading: false,
      error: '',
      nodeInfo: {
        id: 1234,
        name: 'asdf',
        mode: 'OPERATIONAL',
        health: 'OK',
        uptime: 530,
        vendorCode: 1234,
        softwareVersion: '4.3.2.1',
        crc: '0xBEEFALOT',
        hardwareVersion: '0.1.2.4',
        uid: 'my-uid-is-amazing',
        authenticity: 'I AM LEGIT 0x0987'
      }
    }
  },
  mounted () {
    this.refreshData()
  },
  methods: {
    async refreshData () {
      this.error = ''
      this.loading = true

      try {
        const response = await axios.get(ApiRoutes.Nodes.GetDetailsById(this.nodeId))
        this.nodeInfo = response.data
      } catch (e) {
        this.error = e
      }

      this.loading = false
    }
  }
}
</script>

<style scoped>
.fit-border {
  margin-top: 12px;
  margin-left: 22px;
}
</style>
