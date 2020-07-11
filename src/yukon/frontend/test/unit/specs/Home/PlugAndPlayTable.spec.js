/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import PlugAndPlayTable from '@/components/Home/PlugAndPlayTable'
import { mount } from '@vue/test-utils'
import axios from 'axios'
import flushPromises from 'flush-promises'
import ApiRoutes from '@/api/ApiRoutes'

jest.mock('axios', () => {
  return {
    get: jest.fn()
      .mockImplementationOnce(() => ({
        data: {
          '500': 9816439167,
          '352': 9928488809103,
          '101': 21309
        }
      }))
      .mockImplementationOnce(() => Promise.reject(new Error('theerror')))
  }
})

describe('PlugAndPlayTable.vue', () => {
  it('should render correct contents', async () => {
    var wrapper = mount(PlugAndPlayTable) // eslint-disable-line no-unused-vars

    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Bus.PlugAndPlayTable)
  })

  it('should render correct error', async () => {
    var wrapper = mount(PlugAndPlayTable) // eslint-disable-line no-unused-vars

    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Bus.GetInfo)
  })
})
