/*
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { Component, computed, inject, input } from '@angular/core';
import { Surface } from '@a2ui/angular';
import { RendererComponent } from '../../types';
import { UiMessageContent } from '../../../types/ui-message';
import { ChatService } from '../../../services/chat-service';
import { isA2aDataPart } from '../../../utils/type-guards';
import { DataPart } from '@a2a-js/sdk';

@Component({
  selector: 'a2ui-data-part',
  template: `
    @let surface = this.surface();
    @if (surface) {
      <a2ui-surface [surfaceId]="surface.id" [surface]="surface" />
    }
  `,
  standalone: true,
  imports: [Surface],
})
export class A2uiDataPart implements RendererComponent {
  readonly uiMessageContent = input.required<UiMessageContent>();
  private readonly chatService = inject(ChatService);

  protected readonly surface = computed(() => {
    const part = this.uiMessageContent().data;

    if (!isA2aDataPart(part as any)) {
      return undefined;
    }

    // Explicitly cast to DataPart since the predicate above checked it at runtime
    // but didn't narrow the original variable due to 'as any'
    const dataPart = part as DataPart;
    const data = dataPart.data as Record<string, any> | undefined;

    let surfaceId: string | undefined;
    if (data) {
      if (data['surfaceId']) {
        surfaceId = data['surfaceId'];
      } else if (data['createSurface']?.['surfaceId']) {
        surfaceId = data['createSurface']['surfaceId'];
      } else if (data['updateComponents']?.['surfaceId']) {
        surfaceId = data['updateComponents']['surfaceId'];
      }
    }

    if (surfaceId) {
      return this.chatService.a2uiSurfaces().get(surfaceId);
    }
    return undefined;
  });
}
