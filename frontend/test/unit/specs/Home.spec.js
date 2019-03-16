/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import Home from '@/components/Home'
import { mount } from '@vue/test-utils'

describe('Home.vue', () => {
  it('should render correct contents', async () => {
    var wrapper = mount(Home)

    expect(wrapper.find({ ref: 'nodeListTableBody' }).findAll('tr').length).toEqual(5)

    const nodeTableFirstRow = wrapper.find({ ref: 'nodeListTableBody' }).find('tr').findAll('td')
    expect(nodeTableFirstRow.at(0).text()).toEqual('9999')
    expect(nodeTableFirstRow.at(1).text()).toEqual('bnode_0')
    expect(nodeTableFirstRow.at(2).text()).toEqual('OPERATIONAL')
    expect(nodeTableFirstRow.at(3).text()).toEqual('OK')
    expect(nodeTableFirstRow.at(4).text()).toEqual('200')
    expect(nodeTableFirstRow.at(5).text()).toEqual('000')

    // Filter data on:
    // - name
    wrapper.find({ ref: 'textFilter' }).setValue('zZz_')

    expect(wrapper.vm.processedNodes.length).toEqual(1)
    expect(wrapper.vm.processedNodes[0].id).toEqual('6')

    // - id
    wrapper.find({ ref: 'textFilter' }).setValue('99')

    expect(wrapper.vm.processedNodes.length).toEqual(1)
    expect(wrapper.vm.processedNodes[0].id).toEqual('9999')

    // - health
    wrapper.find({ ref: 'textFilter' }).setValue('cRiTICaL')

    expect(wrapper.vm.processedNodes.length).toEqual(1)
    expect(wrapper.vm.processedNodes[0].id).toEqual('6')

    // - mode
    wrapper.find({ ref: 'textFilter' }).setValue('ofFLiNe')

    expect(wrapper.vm.processedNodes.length).toEqual(1)
    expect(wrapper.vm.processedNodes[0].id).toEqual('7')

    // - regex
    wrapper.find({ ref: 'textFilter' }).setValue('.+_.+')

    expect(wrapper.vm.processedNodes.length).toEqual(4)
    expect(wrapper.vm.processedNodes[0].id).toEqual('9999')

    // Sort data on: (sortWay: 'None' implies ascending order)
    // - id
    wrapper.setData({ sortAttribute: 'id' })

    expect(wrapper.vm.processedNodes.length).toEqual(4)
    expect(wrapper.vm.processedNodes[0].id).toEqual('5')
    expect(wrapper.vm.processedNodes[1].id).toEqual('6')

    // - uptime
    wrapper.setData({ sortAttribute: 'uptime' })

    expect(wrapper.vm.processedNodes.length).toEqual(4)
    expect(wrapper.vm.processedNodes[1].id).toEqual('6')
    expect(wrapper.vm.processedNodes[0].id).toEqual('5')

    // - health
    wrapper.setData({ sortAttribute: 'health' })

    expect(wrapper.vm.processedNodes.length).toEqual(4)
    expect(wrapper.vm.processedNodes[0].id).toEqual('9999')
    expect(wrapper.vm.processedNodes[1].id).toEqual('1000')

    // - mode
    wrapper.setData({ sortAttribute: 'mode' })

    expect(wrapper.vm.processedNodes.length).toEqual(4)
    expect(wrapper.vm.processedNodes[0].id).toEqual('9999')
    expect(wrapper.vm.processedNodes[1].id).toEqual('1000')

    // - name
    wrapper.setData({ sortAttribute: 'name' })

    expect(wrapper.vm.processedNodes.length).toEqual(4)
    expect(wrapper.vm.processedNodes[0].id).toEqual('1000')
    expect(wrapper.vm.processedNodes[1].id).toEqual('9999')

    // - vendorCode
    wrapper.setData({ sortAttribute: 'vendorCode' })

    expect(wrapper.vm.processedNodes.length).toEqual(4)
    expect(wrapper.vm.processedNodes[0].id).toEqual('9999')
    expect(wrapper.vm.processedNodes[1].id).toEqual('1000')

    // * test descending order
    wrapper.setData({ sortWay: wrapper.vm.sortWays.descending.name })

    expect(wrapper.vm.processedNodes.length).toEqual(4)
    expect(wrapper.vm.processedNodes[0].id).toEqual('9999')
    expect(wrapper.vm.processedNodes[1].id).toEqual('1000')
  })
})
