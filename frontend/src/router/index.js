import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'

Vue.use(Router)

const AppRoutes = {
  Home: {
    path: '/',
    name: 'Home',
    component: Home
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
