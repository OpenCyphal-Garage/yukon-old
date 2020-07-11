<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <p class='copyable' @click="copy(text)" title='Click to copy'>{{ text }}</p>
</template>

<script>
import copyToClipboard from '@/util/usability.js'

export default {
  name: 'CopyableText',
  propsData: {
   text: 'test'
  },
  methods: {
    copy: text => {
      copyToClipboard(text)
    }
  }
}
</script>

<style>

</style>
