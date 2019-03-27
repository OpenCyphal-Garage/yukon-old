/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import NodeRegisters from '@/components/NodeInfo/NodeRegisters'
import {
  mount
} from '@vue/test-utils'
import axios from 'axios'
import flushPromises from 'flush-promises'
import ApiRoutes from '@/api/ApiRoutes'

jest.mock('axios', () => {
  return {
    get: jest.fn(() => ({
      data: [{
        name: 'nmea.uart_on',
        type: 'boolean',
        value: 'false',
        default: 'false'
      },
      {
        name: 'uavcan.pubp.pres',
        type: 'integer',
        value: 1,
        default: 0,
        min: 0,
        max: 10000
      },
      {
        name: 'pres.variance',
        type: 'real',
        value: 100.5,
        default: 100.0,
        min: 1.0,
        max: 4000.59
      },
      {
        name: 'advertise.as',
        type: 'string',
        value: 'bestnodeinthebus',
        default: 'simplenode'
      }]
    }))
  }
})

describe('NodeRegisters.vue', () => {
  it('should render correct contents and call edit param on tr click', async () => {
    var wrapper = mount(NodeRegisters, {
      propsData: {
        nodeId: 1234
      }
    })

    const editParam = jest.fn()
    wrapper.setMethods({ editParam })

    await flushPromises()

    expect(axios.get).toHaveBeenCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(ApiRoutes.Nodes.GetParametersById(1234))

    // - rendered contents check
    expect(wrapper.find({ ref: 'nodeListParamsTableBody' }).findAll('tr').length).toBe(4)

    // - find first rendered <tr> and click it
    const firstRow = wrapper.find({ ref: 'nodeListParamsTableBody' }).find('tr')
    const tds = firstRow.findAll('td')
    expect(tds.at(0).text()).toEqual('0')
    expect(tds.at(1).text()).toEqual('nmea.uart_on')
    expect(tds.at(2).text()).toEqual('boolean')
    expect(tds.at(3).text()).toEqual('false')
    expect(tds.at(4).text()).toEqual('false')
    expect(tds.at(5).text()).toEqual('')
    expect(tds.at(6).text()).toEqual('')

    firstRow.trigger('click')
    expect(editParam).toHaveBeenCalledTimes(1)
    expect(editParam).toHaveBeenCalledWith({
      name: 'nmea.uart_on',
      type: 'boolean',
      value: 'false',
      default: 'false'
    })
  })
})
