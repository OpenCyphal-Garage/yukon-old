<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
    <div class="ml-4 mb-0">
    <div :if="type !== undefined">
      <p class="mb-0">
        {{ type }}
      </p>

      <div class="ml-4" v-for="k in typeFieldsKeys" :key="type + ':' + k">
        <TypeEditForm v-if="isCompositeType(typeFields[k].type)"
          v-bind:type="typeFields[k].type"
          :parent="stackedParentType + ':' + typeFields[k].type" />

        <div v-else class="ml-4">
            <label :for="type + ':' + k" class="mr-2">
              - {{ k + ' (' + typeFields[k].type + ')'}}
            </label>

            <!-- Root level form input -->
            <div class="float-right">
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import parseDataTypeStringDescriptor from '@/util/dsdl.js'

export default {
  name: 'TypeEditForm',
  props: ['type', 'parent'],
  data () {
    return {
      inputValue: '',
      error: '',
      typeInfo: {
        'uavcan.register.Access.Request': {
          fields: {
            foo: {
              type: 'uavcan.register.Value'
            },
            bar: {
              type: 'saturated int32[<=123]'
            }
          }
        },
        'uavcan.register.Value': {
          fields: {
            first: {
              type: 'bool'
            },
            second: {
              type: 'float32'
            }
          }
        }
      }
    }
  },
  computed: {
    stackedParentType: function () {
      return this.parent === undefined ? this.type : this.parent
    },
    typeFieldsKeys: function () {
      return Object.keys(this.typeInfo[this.type].fields)
    },
    typeFields: function () {
      return this.typeInfo[this.type].fields
    },
    formMetaData: function () {
      if (this.isCompositeType(this.type)) {
        return undefined
      }

      return parseDataTypeStringDescriptor(this.type)
    }
  },
  methods: {
    isCompositeType (type) {
      return type.includes('.')
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

        items.forEach(item => {
          // TODO
        })
      }
    }
  }
}
</script>

<style>
</style>
