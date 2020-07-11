<!--
 * Copyright (C) 2019-2020 UAVCAN Development Team <uavcan.org>
 *               2020  dronesolutions.io. All rights reserved.
 * This software is distributed under the terms of the MIT License.
 *
 * @author Theodoros Ntakouris <zarkopafilis@gmail.com>
 * @author Nuno Marques <nuno.marques@dronesolutions.io>
 -->

<template>
<div>
  <!-- Controls -->
  <div class="row align-items-baseline" style="display: none;">
    <div class="btn-group col-3 pl-0 mr-2 align-items-baseline">
      <input v-model="filter" ref="textFilter" class="form-control" type="text" placeholder="Filter" aria-label="Search">
    </div>

    <div class="form-group mr-2">
      <label for="sortAttribute">Sort on:</label>

      <select v-model="sortAttribute" ref="sortAttribute">
        <option v-for="s in sortAttributes" :key="s">{{ s }}</option>
      </select>
    </div>

    <div class="form-group mr-4">
      <label for="sortWay"> With order: </label>

      <select v-model="sortWay" ref="sortWay">
        <option v-for="s in sortWays" :key="s.name">{{ s.name }}</option>
      </select>
    </div>

    <button type="button" class="btn btn-secondary" @click="clearControls()">Clear</button>
  </div>

  <!-- Nodes List -->
  <h2 style="text-align: center; font-family: Russo One, sans-serif;">Online Nodes</h2>

  <div class="row" style="display: none;">
    <p v-if="error === '' && !loading && processedNodes.length === 0">No nodes found</p>

    <div v-if="!loading && processedNodes.length > 0" class="table-responsive">
      <table class="table table-striped">
        <thead>
          <th>id</th>
          <th>name</th>
          <th>mode</th>
          <th>health</th>
          <th>uptime</th>
          <th>vendor</th>
        </thead>

        <tbody ref="nodeListTableBody">
          <tr v-for="(node) in processedNodes" :key="node.id" @click="viewNodeDetails(node.id)">
            <td>
              <CopyableText v-bind:text="node.id"></CopyableText>
            </td>
            <td>
              <CopyableText v-bind:text="node.name"></CopyableText>
            </td>

            <td :class="node.mode.toLowerCase()">{{ node.mode.toUpperCase() }}</td>
            <td :class="node.health.toLowerCase()">{{ node.health.toUpperCase() }}</td>

            <td>{{ node.uptime }}</td>
            <td>{{ node.vendorCode }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="row">
    <p v-if="error === '' && !loading && processedNodes.length === 0">No nodes found</p>

    <div v-if="!loading && processedNodes.length > 0">
      <v-stage ref="stage" :config="configKonva">
        <v-layer ref="layer">
          <v-group v-for="node in this.nodes" :ref="node.name" :key="node.id" @click="viewNodeDetails(node.id)" @dragmove="updateSubjectLines" @dragend="defaultCursorStyle" @mouseover="highlightNodeBox" @mouseleave="deemphasizeNodeBox" :config="{
                x: getNodePosition(node.id) ? getNodePosition(node.id)[0] : 0,
                y: getNodePosition(node.id) ? getNodePosition(node.id)[1] : 0,
                id: node.id,
                name: node.name,
                draggable: true,
                cache: true
         }">
            <v-rect :config="{
                        width: 300,
                        height: 100,
                        opacity: 0.6,
                        fill: 'white',
                        stroke: 'black',
                        shadowBlur: 10,
                        shadowColor: 'black',
                        shadowOpacity: 0.6
                }"></v-rect>
            <v-circle :config="{
                        x: 20,
                        y: 15,
                        radius: 10,
                        fill: setStatusLedColor(node.health),
                        stroke: 'black',
                        name: node.name,
                        id: node.health
                }"></v-circle>
            <v-text :config="{
                        x: 40,
                        y: 10,
                        fontSize: 16,
                        fontFamily: 'Roboto',
                        text: 'Node ID ' + node.id,
                }"></v-text>
            <v-text :config="{
                        x:140,
                        y:10,
                        fontSize: 16,
                        fontFamily: 'Roboto',
                        text: node.name,
                }"></v-text>
            <v-text :class="node.mode.toLowerCase()" :config="{
                        x:10,
                        y:40,
                        fontSize: 16,
                        fontFamily: 'Roboto',
                        text: 'Mode: ' + node.mode,
                }"></v-text>
          </v-group>
          <v-text ref="topicText" :config="{
                      x: 10,
                      y: 10,
                      fontSize: 20,
                      text: '',
                      fill: 'rgb(37,102,46)',
                      fontFamily: 'Roboto',
                      opacity: 0
            }" />
        </v-layer>
      </v-stage>
    </div>
  </div>

  <div v-if="loading && error.length !== 0" class="row justify-content-center">
    <Spinner></Spinner>
  </div>

  <div class="row">
    <p class="text-center" style="color: red;">{{ error }}</p>
  </div>
</div>
</template>

<script>
import {
  mapState
}
  from 'vuex'
import AppRoutes from '@/Router'
import Spinner from '@/components/Util/Spinner'
import CopyableText from '@/components/Util/CopyableText'

const width = window.innerWidth
const height = window.innerHeight

export default {
  name: 'NodeList',
  components: {
    Spinner,
    CopyableText
  },
  data () {
    return {
      loading: false,
      error: '',
      filter: '',
      sortAttribute: 'None',
      sortWay: 'None',
      sortAttributes: ['None', 'name', 'id', 'uptime', 'vendorCode', 'health', 'mode'],
      sortWays: {
        none: {
          name: 'None'
        },
        ascending: {
          name: 'ascending'
        },
        descending: {
          name: 'descending'
        }
      },
      nodesInitialPosition: [],
      health: {
        OK: 0,
        WARNING: 1,
        ERROR: 2,
        CRITICAL: 3
      },
      mode: {
        OPERATIONAL: 0,
        INITIALIZATION: 1,
        MAINTAINANCE: 2,
        SOFTWARE_UPDATE: 3,
        OFFLINE: 4
      },
      pubPortIDList: [],
      subPortIDList: [],
      nodePubOffset: [],
      healthBlinkLedAnime: [],
      configKonva: {
        width: width,
        height: height
      }
    }
  },
  computed: {
    ...mapState({
      nodes: state => state.nodes.nodeList
    }),
    processedNodes: function () {
      let filtered = this.nodes
      const lowerFilter = this.filter.toLowerCase()

      if (this.filter && this.filter !== '') {
        filtered = filtered.filter(x =>
          x.name.toLowerCase().includes(lowerFilter) || x.name.match(this.filter) || (x.id + '').match(this.filter) ||
          x.health.toLowerCase().includes(lowerFilter) || x.mode.toLowerCase().includes(lowerFilter))
        filtered.sort((a, b) => a.name.indexOf(this.filter) - b.name.indexOf(this.filter))
      }

      if (this.sortAttribute !== 'None' && this.sortAttribute !== 'health' && this.sortAttribute !== 'mode') {
        if (['id', 'uptime', 'vendorCode'].includes(this.sortAttribute)) {
          filtered.sort((a, b) => a[this.sortAttribute] - b[this.sortAttribute])
        } else {
          // eslint-disable-next-line
          filtered.sort((a, b) => {
            if (b[this.sortAttribute] > a[this.sortAttribute]) {
              return -1
            }
            if (b[this.sortAttribute] < a[this.sortAttribute]) {
              return 1
            }
            return 0
          })
        }

        if (this.sortWay === this.sortWays.ascending.name) {
          filtered.reverse()
        }
      } else {
        if (this.sortAttribute === 'health') {
          filtered.sort((a, b) => this.health[a.health] - this.health[b.health])
        } else if (this.sortAttribute === 'mode') {
          filtered.sort((a, b) => this.mode[a.mode] - this.mode[b.mode])
        }
      }

      return filtered
    }
  },
  async mounted () {
    await this.loadData()
    await this.loadPubSub()
    await this.setNodesPositions()
    await this.drawSubjectLines()
    await this.deleteSubjectLines()
    await this.blinkLED()

    const vm = this
    // Run every second
    this.interval = setInterval(async function () {
      await vm.loadPubSub()
      await vm.setNodesPositions()
      await vm.deleteSubjectLines()
      await vm.blinkLED()
      await vm.drawSubjectLines()
      await this.updateSubjectLines
    }, 1000)
  },
  methods: {
    clearControls () {
      this.sortAttribute = 'None'
      this.filter = ''
      this.sortWay = this.sortWays.none.name
    },
    generalSync: async function () {
      await this.blinkLED()
      await this.loadPubSub()
      await this.drawSubjectLines()
      await this.deleteSubjectLines()
      await this.updateSubjectLines
    },
    async loadData () {
      this.error = ''
      this.loading = true
      try {
        await this.$store.dispatch('nodes/getNodeList')
      } catch (e) {
        this.error = e
      }
      this.loading = false
    },
    async loadPubSub () {
      for (var key in this.nodes) {
        if (this.nodes.hasOwnProperty(key)) {
          var pubs = this.nodes[key].publishers
          for (var key2 in pubs) {
            var newPub = {
              id: key,
              name: this.nodes[key].name,
              port_id: pubs[key2].port_id,
              type: pubs[key2].type,
              active: pubs[key2].active
            }

            var idxExistingPub
            const pubExists = this.pubPortIDList.some(function (elem, i) {
              const parsedElem = JSON.parse(JSON.stringify(elem))
              idxExistingPub = i
              return !!(parsedElem.id === newPub.id && parsedElem.name === newPub.name &&
                                      parsedElem.port_id === newPub.port_id &&
                                      parsedElem.type === newPub.type)
            })

            if (this.pubPortIDList.length === 0) {
              this.pubPortIDList.push(newPub)
            } else if (!pubExists) {
              this.pubPortIDList.push(newPub)
            } else if (pubExists && (!pubs[key2].active || pubs[key2].active === 0 || pubs[key2].active === '0')) {
              this.pubPortIDList[idxExistingPub].active = false
            }
          }
        }
      }

      for (var key3 in this.nodes) {
        if (this.nodes.hasOwnProperty(key3)) {
          var subs = this.nodes[key3].subscribers
          for (var key4 in subs) {
            var newSub = {
              id: key3,
              name: this.nodes[key3].name,
              port_id: subs[key4].port_id,
              active: subs[key4].active
            }

            var idxExistingSub
            const subExists = this.subPortIDList.some(function (elem, i) {
              const parsedElem = JSON.parse(JSON.stringify(elem))
              idxExistingSub = i
              return !!(parsedElem.id === newSub.id && parsedElem.name === newSub.name &&
                                      parsedElem.port_id === newSub.port_id &&
                                      parsedElem.type === newSub.type)
            })

            if (this.subPortIDList.length === 0) {
              this.subPortIDList.push(newSub)
            } else if (!subExists) {
              this.subPortIDList.push(newSub)
            } else if (subExists && (!subs[key4].active || subs[key4].active === 0 || subs[key4].active === '0')) {
              this.subPortIDList[idxExistingSub].active = false
            }
          }
        }
      }
    },
    viewNodeDetails (nodeId) {
      this.$router.push({
        name: AppRoutes.NodeDetails.name,
        params: {
          nodeId: nodeId
        }
      })
    },
    generateRandomXPos () {
      return Math.random() * width * 0.75
    },
    generateRandomYPos () {
      return Math.random() * height * 0.75
    },
    getNodePosition (nodeID) {
      for (var node in this.nodesInitialPosition) {
        if (this.nodesInitialPosition[node].id === nodeID && this.nodesInitialPosition[node].hasInitialPosition) {
          return [this.nodesInitialPosition[node].x, this.nodesInitialPosition[node].y]
        }
      }
    },
    async setNodesPositions () {
      for (var node in this.nodes) {
        this.nodesInitialPosition.push({
          id: this.nodes[node].id,
          x: this.generateRandomXPos(),
          y: this.generateRandomYPos(),
          hasInitialPosition: true
        })
      }
    },
    getRectangleBorderPoint (radians, size, xSideOffset, ySideOffset) {
      const width = size.width + xSideOffset * 2
      const height = size.height + ySideOffset * 2

      radians %= 2 * Math.PI
      if (radians < 0) {
        radians += Math.PI * 2
      }

      const phi = Math.atan(height / width)

      let x, y
      if (
        (radians >= 2 * Math.PI - phi && radians <= 2 * Math.PI) ||
        (radians >= 0 && radians <= phi)
      ) {
        x = width / 2
        y = Math.tan(radians) * x
      } else if (radians >= phi && radians <= Math.PI - phi) {
        y = height / 2
        x = y / Math.tan(radians)
      } else if (radians >= Math.PI - phi && radians <= Math.PI + phi) {
        x = -width / 2
        y = Math.tan(radians) * x
      } else if (radians >= Math.PI + phi && radians <= 2 * Math.PI - phi) {
        y = -height / 2
        x = y / Math.tan(radians)
      }

      return {
        x: -Math.round(x),
        y: Math.round(y)
      }
    },
    getCenterLeft (node) {
      return {
        x: node.x() + node.getChildren()[0].width() / 2,
        y: node.y() + node.getChildren()[0].height() / 2
      }
    },
    getCenterRight (node) {
      return {
        x: node.x() + node.getChildren()[0].width() / 2,
        y: node.y() + node.getChildren()[0].height() / 2
      }
    },
    setStatusLedColor (health) {
      if (health === 'OK') {
        return 'rgb(105,228,113)'
      } else if (health === 'WARNING') {
        return 'yellow'
      } else if (health === 'ERROR') {
        return 'red'
      } else if (health === 'CRITICAL') {
        return 'red'
      } else {
        return 'grey'
      }
    },
    async blinkLED () {
      var Konva = require('konva')
      const vm = this

      // Applies to all nodes in stage
      if (typeof this.$refs.layer !== 'undefined') {
        const circleCollection = this.$refs.layer.getNode().find('Circle')

        const amplitude = 1
        const period = 5000

        circleCollection.each(function (shape) {
          const anim = new Konva.Animation(function (frame) {
            shape.setOpacity(
              amplitude * Math.sin((frame.time * 2 * Math.PI) / period)
            )
          }, shape.getLayer())

          if (shape.id() === 'WARNING' || shape.id() === 'CRITICAL') {
            shape.fill(vm.setStatusLedColor(shape.id()))

            if (vm.healthBlinkLedAnime.length === 0 || !vm.healthBlinkLedAnime.some(
              function (elem) { return elem.id === shape.id() && elem.name === shape.name() })) {
              vm.healthBlinkLedAnime.push({
                id: shape.id(),
                name: shape.name(),
                anim: anim
              })

              vm.healthBlinkLedAnime[vm.healthBlinkLedAnime.length - 1].anim.start()
            }
          } else {
            vm.healthBlinkLedAnime.forEach(
              function (elem) {
                if (elem.name === shape.name()) {
                  elem.anim.stop()
                }
              }
            )

            vm.healthBlinkLedAnime = vm.healthBlinkLedAnime.filter(elem => elem.name !== shape.name())
            shape.fill(vm.setStatusLedColor(shape.id()))
          }
        })
      }
    },
    async highlightNodeBox (e) {
      e.target.getStage().container().style.cursor = 'pointer'

      e.target.to({
        shadowColor: 'blue',
        duration: 0.1
      })
    },
    async deemphasizeNodeBox (e) {
      // Applies to all nodes in stage
      e.target.getStage().container().style.cursor = 'default'

      e.target.getLayer().find('Rect').each(function (shape, n) {
        shape.to({
          shadowColor: 'black',
          duration: 0.1
        })
      })
    },
    defaultCursorStyle (e) {
      e.target.getStage().container().style.cursor = 'pointer'
    },
    showPortID (e) {
      const mousePos = this.$refs.stage.getNode().getPointerPosition()
      const topicText = this.$refs.topicText.getNode()

      topicText.setText(e.target.id() + '\n' + e.target.name())
      topicText.setX(mousePos.x)
      topicText.setY(mousePos.y)

      topicText.to({opacity: 1})
      setTimeout(function () {
        topicText.to({opacity: 0})
      }, 1000)
    },
    getPoints (r1, r2, offset) {
      const c1 = this.getCenterRight(r1)
      const c2 = this.getCenterLeft(r2)

      const dx = c1.x - c2.x
      const dy = c1.y - c2.y
      const angle = Math.atan2(-dy, dx)

      const startOffset = this.getRectangleBorderPoint(angle + Math.PI, r1.getChildren()[0].size(), offset, 0)
      const endOffset = this.getRectangleBorderPoint(angle, r2.getChildren()[0].size(), offset, 0)

      const width = r1.getChildren()[0].size().width + offset * 2
      const height = r1.getChildren()[0].size().height + offset * 2

      let radians = angle + Math.PI

      radians %= 2 * Math.PI
      if (radians < 0) {
        radians += Math.PI * 2
      }

      const phi = Math.atan(height / width)

      let start = {
        x: 0,
        y: 0
      }

      let end = {
        x: 0,
        y: 0
      }

      if (
        (radians >= 2 * Math.PI - phi && radians <= 2 * Math.PI) ||
        (radians >= 0 && radians <= phi)
      ) {
        start = {
          x: c1.x - startOffset.x - offset,
          y: c1.y - startOffset.y
        }

        end = {
          x: c2.x - endOffset.x + offset,
          y: c2.y - endOffset.y
        }
      } else if (radians >= phi && radians <= Math.PI - phi) {
        start = {
          x: c1.x - startOffset.x + offset,
          y: c1.y - startOffset.y
        }

        end = {
          x: c2.x - endOffset.x + offset,
          y: c2.y - endOffset.y
        }
      } else if (radians >= Math.PI - phi && radians <= Math.PI + phi) {
        start = {
          x: c1.x - startOffset.x + offset,
          y: c1.y - startOffset.y
        }

        end = {
          x: c2.x - endOffset.x - offset,
          y: c2.y - endOffset.y
        }
      } else if (radians >= Math.PI + phi && radians <= 2 * Math.PI - phi) {
        start = {
          x: c1.x - startOffset.x - offset,
          y: c1.y - startOffset.y
        }

        end = {
          x: c2.x - endOffset.x - offset,
          y: c2.y - endOffset.y
        }
      }

      return [start.x, start.y, end.x, end.y]
    },
    async drawSubjectLines () {
      var Konva = require('konva')

      var offset = 0

      const vm = this

      for (var key in this.pubPortIDList) {
        for (var key2 in this.subPortIDList) {
          // Creates a line between matching port identifiers
          if (this.pubPortIDList[key].name !== this.subPortIDList[key2].name && this.pubPortIDList[key].port_id === this.subPortIDList[key2].port_id) {
            const pubNodeName = this.pubPortIDList[key].name
            const subNodeName = this.subPortIDList[key2].name
            const lineID = pubNodeName + ': ' + this.pubPortIDList[key].port_id

            if (this.nodePubOffset.length === 0 || !this.nodePubOffset.some(
              function (elem) {
                const parsedElem = JSON.parse(JSON.stringify(elem))
                return parsedElem.id === lineID && parsedElem.name === vm.pubPortIDList[key].type
              })) {
              this.nodePubOffset.push({
                id: pubNodeName + ': ' + this.pubPortIDList[key].port_id,
                name: this.pubPortIDList[key].type,
                offset: offset
              })

              var arrow = new Konva.Arrow({
                id: lineID,
                name: this.pubPortIDList[key].type,
                stroke: 'rgb(35,0,179)',
                fill: 'rgb(35,0,179)',
                strokeWidth: 3
              })

              arrow.on('click', this.showPortID)

              const points = this.getPoints(vm.$refs[pubNodeName][0].getNode(), vm.$refs[subNodeName][0].getNode(), offset)
              offset += 15

              arrow.points(points)
              vm.$refs.layer.getNode().add(arrow)
              vm.$refs.layer.getNode().draw()
            }
          }
        }
      }
    },
    async deleteSubjectLines () {
      const vm = this

      if (typeof this.$refs.layer !== 'undefined') {
        const arrowCollection = vm.$refs.layer.getNode().find('Arrow')

        const subjectsToDelete = this.pubPortIDList.filter(function (e) {
          return e.active === false
        })

        arrowCollection.each(function (shape) {
          for (var idx in subjectsToDelete) {
            if (shape.id() === subjectsToDelete[idx].name + ': ' + subjectsToDelete[idx].port_id) {
              shape.to({opacity: 0, duration: 10})

              if (shape.getAbsoluteOpacity() < 0.02) {
                vm.pubPortIDList = vm.pubPortIDList.filter(function (subj) {
                  return (JSON.stringify(subj) !== JSON.stringify(subjectsToDelete[idx]))
                })
                shape.destroy()
              }
            }
          }
        })
      }
    },
    async updateSubjectLines (e) {
      e.target.getStage().container().style.cursor = 'move'

      var offset = 0

      const vm = this

      for (var key in this.pubPortIDList) {
        for (var key2 in this.subPortIDList) {
          // Creates a line between matching port identifiers
          if (this.pubPortIDList[key].name !== this.subPortIDList[key2].name && this.pubPortIDList[key].port_id === this.subPortIDList[key2].port_id) {
            const pubNodeName = this.pubPortIDList[key].name
            const subNodeName = this.subPortIDList[key2].name

            for (var key3 in this.nodePubOffset) {
              if (this.nodePubOffset[key3].id === (pubNodeName + ': ' + vm.pubPortIDList[key].port_id)) {
                offset = this.nodePubOffset[key3].offset
                break
              }
            }

            const points = this.getPoints(vm.$refs[pubNodeName][0].getNode(), vm.$refs[subNodeName][0].getNode(), offset)

            const arrowCollection = this.$refs.layer.getNode().find('Arrow')

            arrowCollection.each(function (shape, n) {
              if (shape.id() === (pubNodeName + ': ' + vm.pubPortIDList[key].port_id)) {
                shape.points(points)
              }
            })
          }
        }
      }
    }
  }
}
</script>
