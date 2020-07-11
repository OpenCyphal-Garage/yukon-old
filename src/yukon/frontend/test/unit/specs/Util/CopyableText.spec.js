/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import CopyableText from '@/components/Util/CopyableText.vue'
import { mount } from '@vue/test-utils'

describe('CopyableText.vue', () => {
  it('should render correct contents and call copyToClipboard on click', async () => {
    var wrapper = mount(CopyableText, {
      props: {
        text: 'dummy'
      }
    })
    wrapper.vm.copy = jest.fn()

    expect(wrapper.find('.copyable').is('p')).toBe(true)
    await wrapper.find('.copyable').trigger('click')

    expect(wrapper.vm.copy).toHaveBeenCalled()
  })
})
