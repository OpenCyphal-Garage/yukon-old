<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div>
    <input v-if="formMetaData.type === 'checkbox'"
      v-model="inputValue"
      type="checkbox"/>

    <input v-else-if="formMetaData.array"
      v-model="inputValue" />

    <input v-else class="float-right type-edit-form"
      v-model="inputValue"
      :type="formMetaData.type"
      :min="formMetaData.min"
      :max="formMetaData.max"
      :step="formMetaData.step"
      :id="stackedParentType + ':' + k"/>

    <p style="color: red; display: inline-block;" v-if="error !== ''"> {{ error }} </p>
  </div>
</template>

<script>
import parseDataTypeStringDescriptor, {isInt, isUint, isFloat} from '@/util/dsdl.js'

export default {
  name: 'TypeInput',
  props: ['type'],
  data () {
    return {
      inputValue: '',
      error: ''
    }
  },
  computed: {
    formMetaData: function () {
      return parseDataTypeStringDescriptor(this.type)
    }
  },
  methods: {
    validateInput () {
      if (this.formMetaData === undefined) {
        return
      }
      this.error = ''

      if (this.formMetaData.array) {
        const contents = this.inputValue.replace(/\s/g, '')
        const items = contents.split(',')

        if (items.length > this.formMetaData.capacity) {
          this.error = `Exceeded max array capacity (${items.length} > ${this.formMetaData.capacity})`
          return
        }

        items.forEach(item => {
          // correct type checks
          if (this.formMetaData.primitiveType === 'uint') {
            if (!isUint(item)) {
              this.error = `'${item}' is not uint`
              return
            }
          }

          if (this.formMetaData.primitiveType === 'int') {
            if (!isInt(item)) {
              this.error = `'${item}' is not int`
              return
            }
          }

          if (this.formMetaData.primitiveType === 'float') {
            if (!isFloat(item)) {
              this.error = `'${item}' is not float`
              return
            }
          }

          // bound checks
          const number = Number(item)
          if (number <= this.formMetaData.min) {
            this.error = `'${number}' must be >= ${this.formMetaData.min}`
            return
          }

          if (number >= this.formMetaData.max) {
            this.error = `'${number}' must be <= ${this.formMetaData.max}`
            return
          }

          this.error = ''
        })
      }
    }
  }
}
</script>

<style>

</style>
