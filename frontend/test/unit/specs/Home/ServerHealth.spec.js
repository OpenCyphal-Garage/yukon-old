/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import ServerHealth from '@/components/Home/ServerHealth'
import { mount } from '@vue/test-utils'
import axios from 'axios'
import flushPromises from 'flush-promises'
import ApiRoutes from '@/api/ApiRoutes'

jest.mock('axios', () => {
  return {
    get: jest.fn()
      .mockImplementationOnce(() => ({
        health: {
          uptime: 1000,
          health: 'Health is good',
          version: '1.2.3'
        }
      }))
      .mockImplementationOnce(() => Promise.reject(new Error('theerror')))
  }
})

describe('ServerHealth.vue', () => {
  it('should render correct contents', async () => {
    var wrapper = mount(ServerHealth)

    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.General.Health)

    const html = wrapper.html().toLowerCase()
    const includes = ['uptime', 1000, 'health is good', '1.2.3']

    includes.forEach(x => expect(html.includes(x)))
  })

  it('should render correct error', async () => {
    var wrapper = mount(ServerHealth)

    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Bus.GetInfo)

    const html = wrapper.html().toLowerCase()
    const includes = ['uptime', 1000, 'health is good', '1.2.3']

    includes.forEach(x => !expect(html.includes(x)))

    expect(html.includes('theerror'))
  })
})
