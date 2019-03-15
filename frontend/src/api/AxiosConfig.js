/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import axios from 'axios'

export default function configureAxios () {
  axios.interceptors.response.use(undefined, function (error) {
    // Log all errors in that format
    console.log(`Axios Error: ${JSON.stringify(error)}`)
    return Promise.reject(error)
  })
}
