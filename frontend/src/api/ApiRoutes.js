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
<<<<<<< HEAD
    GetDetailsById: nodeId => NodesBase + '/' + nodeId,
    GetParametersById: nodeId => NodesBase + '/' + nodeId + '/parameters',
    UpdateParameterById: (nodeId, param) => NodesBase + '/' + nodeId + '/parameters/' + param
=======
    GetById: nodeId => NodesBase + '/' + nodeId
>>>>>>> 05128e58e1429b500db0c421d0b4c9a18ff6086e
  }
}

export default ApiRoutes
