/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import NodeConstants from '@/components/NodeInfo/NodeConstants'
import {
  mount
} from '@vue/test-utils'
import axios from 'axios'
import flushPromises from 'flush-promises'
import ApiRoutes from '@/api/ApiRoutes'

jest.mock('axios', () => {
  return {
    get: jest.fn(() => ({
      data: {
        id: 1234,
        name: 'asdf',
        mode: 'OPERATIONAL',
        health: 'OK',
        uptime: 530,
        vendorCode: 1234,
        softwareVersion: '4.3.2.1',
        crc: '0xBEEFALOT',
        hardwareVersion: '0.1.2.4',
        uid: 'my-uid-is-amazing',
        authenticity: 'I AM LEGIT 0x0987'
      }
    }))
  }
})

describe('NodeConstants.vue', () => {
  it('should render correct contents', async () => {
    var wrapper = mount(NodeConstants, {
      propsData: {
        nodeId: 1234
      }
    })

    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Nodes.GetDetailsById(1234))

    const text = wrapper.text()
    expect(text.includes('1234')).toBe(true)
    expect(text.includes('asdf')).toBe(true)
    expect(text.includes('OPERATIONAL')).toBe(true)
    expect(text.includes('OK')).toBe(true)
    expect(text.includes(530)).toBe(true)
    expect(text.includes(1234)).toBe(true)
    expect(text.includes('4.3.2.1')).toBe(true)
    expect(text.includes('0xBEEFALOT')).toBe(true)
    expect(text.includes('0.1.2.4')).toBe(true)
    expect(text.includes('my-uid-is-amazing')).toBe(true)
    expect(text.includes('I AM LEGIT 0x0987')).toBe(true)
  })
})
