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
      v-model="inputValue"
      v-on:input="validateInput()" />

    <input v-else class="float-right type-edit-form"
      v-model="inputValue"
      :type="formMetaData.type"
      :min="formMetaData.min"
      :max="formMetaData.max"
      :step="formMetaData.step"/>

    <p style="color: red; display: inline-block;" v-if="error !== ''"> {{ error }} </p>
  </div>
</template>

<script>
import parseDataTypeStringDescriptor, { isInt, isUint, isFloat } from '@/util/dsdl.js'

export default {
  name: 'TypeInput',
  props: ['type', 'name'],
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
    getValue () { // returns the value for this type-input component
      const ret = {}
      ret[this.name] = ''

      if (this.formMetaData.type === 'checkbox') {
        ret[this.name] = this.inputValue ? 1 : 0
      }

      if (this.formMetaData.array) {
        const contents = this.inputValue.replace(/\s/g, '')

        if (contents !== '') {
          const items = contents.split(',')
          ret[this.name] = items.map(x => parseFloat(x))
        } else {
          ret[this.name] = []
        }
      }

      if (['uint', 'int', 'float'].includes(this.formMetaData.type)) {
        ret[this.name] = parseFloat(this.inputValue)
      }
      return ret
    },
    hasError () {
      return this.error !== ''
    },
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

        if (items.length === 0 || items[0].replace(' ', '') === '') {
          this.error = ''
          return // empty array
        }

        let err = ''
        items.forEach(item => {
          // correct type checks
          if (this.formMetaData.primitiveType === 'uint') {
            if (!isUint(item)) {
              err = `'${item}' is not uint`
              return
            }
          }

          if (this.formMetaData.primitiveType === 'int') {
            if (!isInt(item)) {
              err = `'${item}' is not int`
              return
            }
          }

          if (this.formMetaData.primitiveType === 'float') {
            if (!isFloat(item)) {
              err = `'${item}' is not float`
              return
            }
          }

          // min-max bound checks
          const number = parseFloat(item)
          if (number <= this.formMetaData.min) {
            err = `'${number}' must be >= ${this.formMetaData.min}`
            return
          }

          if (number >= this.formMetaData.max) {
            err = `'${number}' must be <= ${this.formMetaData.max}`
          }
        })

        this.error = err
      }
    }
  }
}
</script>

<style>

</style>
