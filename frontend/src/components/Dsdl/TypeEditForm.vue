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
            <input class="float-right"
            :id="stackedParentType + ':' + k"
            required />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TypeEditForm',
  props: ['type', 'parent'],
  data () {
    return {
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
    }
  },
  methods: {
    isCompositeType (type) {
      return type.includes('.')
    }
  }
}
</script>

<style>
</style>
