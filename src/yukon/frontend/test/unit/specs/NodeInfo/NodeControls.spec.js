/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import NodeControls from '@/components/NodeInfo/NodeControls'
import { mount, createLocalVue } from '@vue/test-utils'
import axios from 'axios'
import ApiRoutes from '@/api/ApiRoutes'
import flushPromises from 'flush-promises'
import Vuex from 'vuex'

jest.mock('axios', () => {
  return {
    post: jest.fn()
  }
})

describe('NodeControls.vue', () => {
  const localVue = createLocalVue()

  localVue.use(Vuex)

  it('should call correct endpoints on button click', async () => {
    var wrapper = mount(NodeControls, {
      propsData: {
        nodeId: 1234
      }
    }, localVue)

    await flushPromises()

    expect(wrapper.find({ref: 'restartButton'}).is('button')).toBe(true)
    wrapper.find({ref: 'restartButton'}).trigger('click')

    expect(axios.post).toHaveBeenCalledTimes(1)
    expect(axios.post).toHaveBeenCalledWith(ApiRoutes.Nodes.RestartById(1234))

    expect(wrapper.find({ref: 'startFirmwareUpdateButton'}).is('button')).toBe(true)
    wrapper.find({ref: 'startFirmwareUpdateButton'}).trigger('click')

    expect(axios.post).toHaveBeenCalledTimes(2)
    expect(axios.post).toHaveBeenCalledWith(ApiRoutes.Nodes.StartFirmwareUpdateById(1234))
  })
})
