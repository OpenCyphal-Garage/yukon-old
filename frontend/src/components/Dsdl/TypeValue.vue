<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div class="ml-4 mb-0">
    <div :if="val !== undefined">
      <p class="mb-0">
        {{ displayName }}
      </p>
      <div class="ml-2" v-for="k in keys" :key="k">
        <TypeValue v-if="val[k]._type_ !== undefined" v-bind:val="val[k]"/>

        <p class="ml-4 mb-0" v-else-if="k !== '_type_'"> <!-- Ignore _type_ -->
          {{ "- " + k + ": " + val[k] }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TypeValue',
  props: ['val'],
  computed: {
    keys: function () {
      return Object.keys(this.val)
    },
    displayName: function () {
      return this.val._type_ === undefined ? '' : this.val._type_.join('.') + ' :'
    }
  }
}
</script>

<style>
</style>
