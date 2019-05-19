/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import BusInfo from '@/components/Home/BusInfo'
import { mount } from '@vue/test-utils'
import axios from 'axios'
import flushPromises from 'flush-promises'
import ApiRoutes from '@/api/ApiRoutes'

jest.mock('axios', () => {
  return {
    get: jest.fn()
      .mockImplementationOnce(() => ({
        data: {
          resilience: 1,
          name: 'cansocket',
          protocol: 'CanFD'
        }
      }))
      .mockImplementationOnce(() => Promise.reject(new Error('theerror')))
  }
})

describe('BusInfo.vue', () => {
  it('should render correct contents', async () => {
    var wrapper = mount(BusInfo)

    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Bus.GetInfo)

    const html = wrapper.html().toLowerCase()
    const includes = ['resilience', 1, 'CanFD', 'cansocket']

    includes.forEach(x => expect(html.includes(x)))
  })

  it('should render correct error', async () => {
    var wrapper = mount(BusInfo)

    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Bus.GetInfo)

    const html = wrapper.html().toLowerCase()
    const includes = ['resilience', 1, 'CanFD', 'cansocket']

    includes.forEach(x => !expect(html.includes(x)))

    expect(html.includes('theerror'))
  })
})
