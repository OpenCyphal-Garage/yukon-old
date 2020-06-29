/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

const ApiBaseUrl = process.env.API_URL
const BasePrefix = '/api'

const Base = ApiBaseUrl + BasePrefix + '/v1'
const NodesBase = Base + '/nodes'
const TypesBase = Base + '/types'
const BusBase = Base + '/bus'

const ApiRoutes = {
  ApiBaseUrl: ApiBaseUrl,
  Nodes: {
    GetAll: NodesBase,
    GetDetailsById: nodeId => NodesBase + '/' + nodeId,
    RestartById: nodeId => NodesBase + '/' + nodeId + '/restart',
    StartFirmwareUpdateById: nodeId => NodesBase + '/' + nodeId + '/firmwareupdate',
    GetRegistersById: nodeId => NodesBase + '/' + nodeId + '/registers',
    UpdateRegisterByIdAndName: (nodeId, param) => NodesBase + '/' + nodeId + '/registers/' + param,
    GetPlugAndPlayTable: NodesBase + '/plugandplay',
    GetGlobalRegisterView: NodesBase + '/grv'
  },
  General: {
    Health: Base + '/health'
  },
  Types: {
    GetTypeInfoByName: type => TypesBase + '/' + type
  },
  Bus: {
    GetInfo: BusBase,
    Monitor: BusBase + '/monitor'
  },
  EventSource: Base + '/eventSource'
}

export default ApiRoutes
