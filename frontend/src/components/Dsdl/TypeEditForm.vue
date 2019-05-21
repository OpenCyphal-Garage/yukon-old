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
        {{ `${(name ? `- ${name}:  ` : '')}${type}` }}
      </p>

      <div class="ml-4" v-for="k in typeFieldKeys" :key="type + ':' + k">
        <TypeEditForm v-if="isCompositeType(typeFields[k].type)"
          :ref="typeFields[k].type"
          :type="typeFields[k].type"
          :name="k"
          :parent="stackedParentType + ':' + typeFields[k].type" />

        <div v-else class="ml-4"> <!-- k (name) is leaf -->
            <label :for="type + ':' + k" class="mr-2">
              - {{ k + ':  (' + typeFields[k].type + ')'}}
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
import {mapState} from 'vuex'

export default {
  name: 'TypeEditForm',
  props: ['type', 'parent', 'name'],
  components: {
    TypeInput
  },
  async mounted () {
    await this.loadTypeInfo()
  },
  computed: {
    ...mapState({
      typeInfo: state => state.types.typeInfo
    }),
    stackedParentType: function () {
      return this.parent === undefined ? this.type : (this.parent ? this.parent : '')
    },
    typeFieldKeys: function () {
      const obj = this.typeInfo[this.type]
      if (!obj) {
        return []
      }

      const fields = obj.fields
      if (!fields) {
        console.log(this.typeInfo[this.type])
        return []
      }

      return Object.keys(fields)
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

      if (!this.name) {
        return ret
      }

      const val = {}
      val[this.name] = ret

      return val
    },
    async loadTypeInfo () {
      await this.$store.dispatch('types/getTypeInfo', this.type)
    }
  }
}
</script>

<style>
</style>
