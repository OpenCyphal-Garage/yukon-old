<!--
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 -->

<template>
  <div style="font-family: 'Roboto';">
    <div class="d-flex flex-row">
      <h3 class="p-2 mr-3">
        Subscriptions
      </h3>

      <div class="p-2">
        <input v-model="portId" class="form-control" type="number" min="0" max="65535" placeholder="Port ID" aria-label="Search">
      </div>

      <div class="w-25 p-2">
        <input v-model="dataType" class="form-control col-xs-2" type="text" placeholder="Data Type" aria-label="Search">
      </div>

      <div class="w-25 p-2">
        <input v-model="requestObject" class="form-control col-xs-4" type="text" placeholder="Optional Request Object" aria-label="Search">
      </div>

      <button type="button" class="btn btn-link align-self-center" @click="addDataTarget">Add</button>
    </div>

    <div class="d-flex flex-row" v-for="dataTarget in dataTargets" :key="dataTarget.name">
    </div>

    <div v-if="dataTargets.length > 0" class="table-responsive">
      <table class="table table-striped table-sm">
        <thead>
          <th>portId</th>
          <th>dataType</th>
          <th>requestObject</th>
          <th>Actions</th>
        </thead>

        <tbody>
          <tr v-for="dataTarget in dataTargets" :key="'' + dataTarget.portId + dataTarget.dataType + dataTarget.requestObject">
            <td> {{ dataTarget.portId }}</td>
            <td> {{ dataTarget.dataType }}</td>
            <td> {{ dataTarget.requestObject }}</td>
            <td>
              <button type="button" class="btn btn-link" @click="removeDataTarget(dataTarget)">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="d-flex flex-row">
      <h3 class="p-2 mr-3 align-self-baseline">
        Value Extractors
      </h3>

      <div class="p-2">
        <select v-model="selectedMappingTarget">
          <option
            v-for="mappingTarget in availableMappingTargets" :key="mappingTarget.displayName" :value="mappingTarget">{{ mappingTarget.displayName }}</option>
        </select>
      </div>

      <div class="p-2">
        <input v-model="scalarExtractor" class="form-control" type="text" min="0" max="65535" placeholder="Scalar Extractor" aria-label="Search">
      </div>

      <button type="button" class="btn btn-link align-self-center" @click="addScalarExtractor">Add</button>
    </div>

    <div v-if="scalarTargets.length > 0" class="table-responsive">
      <table class="table table-striped table-sm">
        <thead>
          <th>from</th>
          <th>extract</th>
          <th>Actions</th>
        </thead>

        <tbody>
          <tr v-for="(e, index) in scalarTargets" :key="e.mappingTarget.displayName + '[' + e.scalarExtractor + ']'">
            <td> {{ e.mappingTarget.displayName }}</td>
            <td> {{ e.scalarExtractor }}</td>
            <td>
              <button type="button" class="btn btn-link" @click="removeScalarExtractor(index)">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="d-flex flex-row">
      <h3 class="p-2 align-self-baseline">Plot Type</h3>

      <div class="p-2 align-self-center">
        <select v-model="selectedPlotType">
          <option
            v-for="plot in plotTypes" :key="plot.name" :value="plot">{{ plot.name }}</option>
        </select>
      </div>

    </div>

    <hr />

    <div class="row ml-2">
      <component v-bind:is="selectedPlotType.component"></component>
    </div>
  </div>
</template>

<script>
import TimeY from './Renderers/TimeY'
import XY from './Renderers/XY'

export default {
  name: 'Plotter',
  data () {
    return {
      portId: '',
      dataType: '',
      requestObject: '',
      dataTargets: [],
      scalarExtractor: '',
      selectedMappingTarget: {},
      scalarTargets: [],
      plotData: [],
      scalarPlotVector: [],
      plotTypes: [{
        name: 'Time-Y',
        component: TimeY
      },
      {
        name: 'X-Y',
        component: XY
      }],
      selectedPlotType: { name: 'Time-Y' }
    }
  },
  mounted () {

  },
  computed: {
    pipelineModelStateCorrect: function () {
      return true
    },
    availableMappingTargets: function () {
      return this.dataTargets.map(dataTarget => {
        return {
          displayName: dataTarget.portId + '.' + dataTarget.dataType + (dataTarget.requestObject !== '' ? '->' + dataTarget.requestObject : ''),
          target: dataTarget
        }
      })
    }
  },
  methods: {
    addDataTarget () {
      if (this.portId.trim() === '') {
        return
      }

      if (this.dataType.trim() === '') {
        return
      }

      this.dataTargets.push({ portId: this.portId, dataType: this.dataType, requestObject: this.requestObject })

      this.portId = ''
      this.dataType = ''
      this.requestObject = ''
    },
    removeDataTarget (dataTarget) {
      const newDataTargets = this.dataTargets.filter(x => {
        const diffPortId = x.portId !== dataTarget.portId
        const diffDataType = x.dataType !== dataTarget.dataType
        const diffRequestObject = x.requestObject !== dataTarget.requestObject

        return diffPortId || diffDataType || diffRequestObject
      })

      this.dataTargets = newDataTargets
    },
    addScalarExtractor () {
      if (this.selectedMappingTarget === undefined || this.selectedMappingTarget === {}) {
        return
      }

      if (this.scalarExtractor.trim === '') {
        return
      }

      this.scalarTargets.push({ mappingTarget: this.selectedMappingTarget, scalarExtractor: this.scalarExtractor })

      this.selectedMappingTarget = {}
      this.scalarExtractor = ''
    },
    removeScalarExtractor (index) {
      this.scalarTargets.splice(index, 1)
    }
  }
}
</script>

<style>

</style>
