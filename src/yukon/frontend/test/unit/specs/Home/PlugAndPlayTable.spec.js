/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import PlugAndPlayTable from '@/components/Home/PlugAndPlayTable'
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
          '500': 9816439167,
          '352': 9928488809103,
          '101': 21309
        }
      }))
      .mockImplementationOnce(() => Promise.reject(new Error('theerror')))
  }
})

describe('PlugAndPlayTable.vue', () => {
  let wrapper;
  let store;

  const localVue = createLocalVue();

  localVue.use(Vuex);

  beforeEach(() => {
    store = vuexstore;
    wrapper = mount(PlugAndPlayTable, { store, localVue });
  });

  it('should render correct contents', async () => {
    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Bus.PlugAndPlayTable)
  })

  it('should render correct error', async () => {
    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Bus.GetInfo)
  })
})
