/**
 * Copyright (C) 2019-2020 UAVCAN Development Team <uavcan.org>
 *               2020  dronesolutions.io. All rights reserved.
 * This software is distributed under the terms of the MIT License.
 *
 * @author Theodoros Ntakouris <zarkopafilis@gmail.com>
 * @author Nuno Marques <nuno.marques@dronesolutions.io>
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

import VueKonva from 'vue-konva'

Vue.use(BootstrapVue)
Vue.use(VueTruncate)
Vue.use(underscore)
Vue.use(VueKonva)

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
