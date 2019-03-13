const BasePrefix = '/api'

const ApiBaseUrl = process.env.API_URL
const Base = ApiBaseUrl + BasePrefix + '/v1'
const NodesBase = Base + '/nodes'

const ApiRoutes = {
  ApiBaseUrl: ApiBaseUrl,
  Nodes: {
    GetAll: NodesBase,
    GetById: nodeId => NodesBase + '/' + nodeId
  }
}

export default ApiRoutes
