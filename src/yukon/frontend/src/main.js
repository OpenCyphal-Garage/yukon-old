/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import Vue from 'vue'
import store from '@/store'

import App from '@/App'
import {AppRouter} from '@/Router'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import BootstrapVue from 'bootstrap-vue'

import VueTruncate from 'vue-truncate-filter'
import configureAxios from '@/api/AxiosConfig'
import configureEventSource from '@/api/eventsource'

import underscore from 'vue-underscore'

Vue.use(BootstrapVue)
Vue.use(VueTruncate)
Vue.use(underscore)

configureAxios()
configureEventSource()

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store: store,
  router: AppRouter,
  components: { App },
  template: '<App/>'
})
