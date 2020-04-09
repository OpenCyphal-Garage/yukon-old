/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import NodeControls from '@/components/NodeInfo/NodeControls'
import {
  mount
} from '@vue/test-utils'
import axios from 'axios'
import flushPromises from 'flush-promises'
import ApiRoutes from '@/api/ApiRoutes'

jest.mock('axios', () => {
  return {
    post: jest.fn()
  }
})

describe('NodeControls.vue', () => {
  it('should call correct endpoints on button click', async () => {
    var wrapper = mount(NodeControls, {
      propsData: {
        nodeId: 1234
      }
    })

    await flushPromises()

    expect(wrapper.find({ ref: 'restartButton' }).is('button')).toBe(true)
    wrapper.find({ ref: 'restartButton' }).trigger('click')

    expect(axios.post).toHaveBeenCalledTimes(1)
    expect(axios.post).toHaveBeenCalledWith(ApiRoutes.Nodes.RestartById(1234))

    expect(wrapper.find({ ref: 'startFirmwareUpdateButton' }).is('button')).toBe(true)
    wrapper.find({ ref: 'startFirmwareUpdateButton' }).trigger('click')

    expect(axios.post).toHaveBeenCalledTimes(2)
    expect(axios.post).toHaveBeenCalledWith(ApiRoutes.Nodes.StartFirmwareUpdateById(1234))
  })
})
