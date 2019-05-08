import { shallowMount } from '@vue/test-utils'
import Home from '@/components/Home/Home'

import BusInfo from '@/components/Home/BusInfo'
import ServerHealth from '@/components/Home/ServerHealth'
import PlugAndPlayTable from '@/components/Home/PlugAndPlayTable'
import NodeList from '@/components/Home/NodeList'

describe('Home.vue', () => {
  it('renders correct subcomponents', () => {
    const wrapper = shallowMount(Home, {})
    const contents = [BusInfo, ServerHealth, PlugAndPlayTable, NodeList]

    contents.forEach(comp => {
      expect(wrapper.find(comp).exists())
    })
  })
})
