/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import { mount } from '@vue/test-utils'
import Spinner from '@/components/Spinner.vue'

describe('Spinner.vue', () => {
  it('should render correct contents', () => {
    const wrapper = mount(Spinner)

    expect(wrapper.classes()).toContain('spinner')
    expect(wrapper.find('.fingerprint-spinner').classes()).toContain('fingerprint-spinner')
  })
})
