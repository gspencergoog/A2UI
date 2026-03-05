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
      } else if (data['beginRendering']?.['surfaceId']) {
        surfaceId = data['beginRendering']['surfaceId'];
      } else if (data['surfaceUpdate']?.['surfaceId']) {
        surfaceId = data['surfaceUpdate']['surfaceId'];
      }
    }

    if (surfaceId) {
      return this.chatService.a2uiSurfaces().get(surfaceId);
    }
    return undefined;
  });
}
