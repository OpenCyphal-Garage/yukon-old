import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home/Home'
import NodeInfoPage from '@/components/NodeInfo/NodeInfoPage'
import GlobalRegisterView from '@/components/GlobalRegisterView/GlobalRegisterView'
import Plotter from '@/components/Plotter/Plotter'

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
    props: true
  },
  GlobalRegisterView: {
    path: '/registers',
    name: 'Global Register View',
    component: GlobalRegisterView
  },
  Plotter: {
    path: '/plotter',
    name: 'Plotter',
    component: Plotter
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
