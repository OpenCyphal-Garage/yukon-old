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

    <div class="row ml-4 mb-2">
      <button @click="tryUpdateRegister()" class="btn btn-primary">Update {{ register }}</button>
      <p class="ml-1" style="color: red;" :if="error !== ''"> {{ error }} </p>
    </div>
  </div>
</template>

<script>
import TypeEditForm from '@/components/Dsdl/TypeEditForm'

export default {
  name: 'RegisterWorkset',
  props: ['register', 'type'],
  components: {
    TypeEditForm
  },
  data () {
    return {
      error: '',
      loading: false
    }
  },
  methods: {
    async tryUpdateRegister () {
      const typeValueComponent = this.$refs.form

      this.error = ''
      if (typeValueComponent.hasError()) {
        this.error = 'Please fix all errors before updating the register'
      }

      const value = typeValueComponent.getValue()
      await this.updateRegister(value)
    },
    async updateRegister (value) {
      console.log(value)
    }
  }
}
</script>

<style>

</style>
