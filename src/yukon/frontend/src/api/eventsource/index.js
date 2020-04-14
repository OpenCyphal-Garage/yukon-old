/*
 * Copyright (C) 2019 UAVCAN Development Team  <uavcan.org>
 * This software is distributed under the terms of the MIT License.
 *
 * Author: Theodoros Ntakouris <zarkopafilis@gmail.com>
 */

import ApiRoutes from '@/api/ApiRoutes'
import Handlers from './handlers'

export default function configureEventSources () {
  const eventSource = new EventSource(ApiRoutes.EventSource)
  for (const handler of Handlers) {
    eventSource.addEventListener(handler.eventType, event => {
      handler.handle(event)
    })
  }
}
