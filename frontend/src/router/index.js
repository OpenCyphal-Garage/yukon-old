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

const AppRouter = new Router({
  routes: Object.values(AppRoutes)
})

export default {AppRouter, AppRoutes}
