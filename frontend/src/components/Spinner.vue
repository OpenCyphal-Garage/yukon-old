<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div class="spinner">
      <fingerprint-spinner
        :animation-duration="1500"
        :size="60"
        :color="'#3366ff'" />
  </div>
</template>

<script>
import {FingerprintSpinner} from 'epic-spinners'
export default {
  name: 'Spinner',
  components: {
    FingerprintSpinner
  }
}
</script>

<style>

</style>
