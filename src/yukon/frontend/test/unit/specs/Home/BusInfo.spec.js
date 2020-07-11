/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import BusInfo from '@/components/Home/BusInfo'
import { mount, createLocalVue } from '@vue/test-utils'
import axios from 'axios'
import ApiRoutes from '@/api/ApiRoutes'
import flushPromises from 'flush-promises'
import vuexstore from '@/store/index'
import Vuex from 'vuex'

jest.mock('axios', () => {
  return {
    get: jest.fn()
      .mockImplementationOnce(() => ({
        data: {
          resilience: 1,
          name: 'socketcan0',
          transport: 'CAN'
        }
      }))
      .mockImplementationOnce(() => Promise.reject(new Error('theerror')))
  }
})

describe('BusInfo.vue', () => {
  let wrapper
  let store

  const localVue = createLocalVue()

  localVue.use(Vuex)

  beforeEach(() => {
    store = vuexstore
    wrapper = mount(BusInfo, { store, localVue })
  })

  it('should render correct contents', async () => {
    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Bus.GetInfo)

    const html = wrapper.html().toLowerCase()
    const includes = ['resilience', 1, 'CanFD', 'cansocket']

    includes.forEach(x => expect(html.includes(x)))
  })

  it('should render correct error', async () => {
    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Bus.GetInfo)

    const html = wrapper.html().toLowerCase()
    const includes = ['resilience', 1, 'CanFD', 'cansocket']

    includes.forEach(x => !expect(html.includes(x)))

    expect(html.includes('theerror'))
  })
})
