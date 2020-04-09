/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import CopyableText from '@/components/Util/CopyableText.vue'
import {
  mount
} from '@vue/test-utils'

describe('CopyableText.vue', () => {
  it('should render correct contents and call copyToClipboard on click', () => {
    var wrapper = mount(CopyableText, {
      propsData: {
        text: 'dummy'
      }
    })
    const copyToClipboard = jest.fn()
    wrapper.setMethods({ copyToClipboard })

    expect(wrapper.find('.copyable').is('p')).toBe(true)
    wrapper.find('.copyable').trigger('click')

    expect(copyToClipboard).toBeCalledWith('dummy')
  })
})
