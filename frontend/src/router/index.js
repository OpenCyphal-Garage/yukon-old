import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import NodeInfoPage from '@/components/NodeInfo/NodeInfoPage'

Vue.use(Router)

const AppRoutes = {
  Home: {
    path: '/',
    name: 'Home',
    component: Home
  },
  NodeDetails: {
    path: '/nodes/:nodeId',
    name: 'Node Details',
    component: NodeInfoPage,
    props: true,
    of: nodeId => '/nodes/' + nodeId
  }
}

export const AppRouter = new Router({
  routes: Object.values(AppRoutes)
})

AppRouter.beforeEach((to, from, next) => {
  document.title = `Yukon: ${to.name}`
  next()
})

export default AppRoutes
