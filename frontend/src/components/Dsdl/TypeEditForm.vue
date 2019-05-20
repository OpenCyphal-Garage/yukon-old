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
          :ref="typeFields[k].type"
          :type="typeFields[k].type"
          :parent="stackedParentType + ':' + typeFields[k].type" />

        <div v-else class="ml-4"> <!-- k (name) is leaf -->
            <label :for="type + ':' + k" class="mr-2">
              - {{ k + ' (' + typeFields[k].type + ')'}}
            </label>

            <!-- Root level form actual input -->
            <div class="float-right">
              <TypeInput :type="typeFields[k].type" :name="k"
                :ref="k + ':' + typeFields[k].type" />
            </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import TypeInput from './TypeInput'

export default {
  name: 'TypeEditForm',
  props: ['type', 'parent'],
  components: {
    TypeInput
  },
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
      return this.parent === undefined ? this.type : (this.parent ? this.parent : '')
    },
    typeFieldsKeys: function () {
      return Object.keys(this.typeInfo[this.type].fields)
    },
    typeFields: function () {
      const fields = this.typeInfo[this.type].fields
      return fields !== undefined ? fields : []
    }
  },
  methods: {
    isCompositeType (type) {
      return type !== undefined && type.includes('.')
    },
    hasError () {
      return Object.values(this.$refs).map(r => r[0])
        .reduce((acc, cur) => acc || cur.hasError(), false)
    },
    getValue () {
      let ret = {}
      Object.values(this.$refs).forEach(r => {
        const ref = r[0]
        if (ref.getValue !== undefined) {
          ret = {
            ...ret,
            ...ref.getValue()
          }
        }
      })

      if (this.parent === undefined) {
        return ret
      }

      const val = {}
      val[this.type] = ret

      return val
    }
  }
}
</script>

<style>
</style>
