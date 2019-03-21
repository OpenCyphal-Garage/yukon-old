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

const ApiRoutes = {
  ApiBaseUrl: ApiBaseUrl,
  Nodes: {
    GetAll: NodesBase,
    GetDetailsById: nodeId => NodesBase + '/' + nodeId,
    ShutdownById: nodeId => NodesBase + '/' + nodeId + '/shutdown',
    StartFirmwareUpdateById: nodeId => NodesBase + '/' + nodeId + '/firmwareupdate',
    GetParametersById: nodeId => NodesBase + '/' + nodeId + '/parameters',
    UpdateParameterById: (nodeId, param) => NodesBase + '/' + nodeId + '/parameters/' + param
  }
}

export default ApiRoutes
