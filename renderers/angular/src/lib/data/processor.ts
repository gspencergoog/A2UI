/*
 Copyright 2025 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

import { MessageProcessor as A2uiMessageProcessor } from '@a2ui/web_core/v0_9';
import * as Types from '@a2ui/web_core/v0_9';
import { BASIC_FUNCTIONS } from '@a2ui/web_core/v0_9';
import { Inject, Injectable } from '@angular/core';
import { firstValueFrom, Subject } from 'rxjs';
import { Catalog } from '../rendering/catalog';

export interface A2uiClientMessage {
  action: Types.Action;
  version: 'v0.9';
  surfaceId?: string;
}

export interface DispatchedEvent {
  message: A2uiClientMessage;
  completion: Subject<Types.A2uiMessage[]>;
}

@Injectable({ providedIn: 'root' })
export class MessageProcessor extends A2uiMessageProcessor<any> {
  constructor(@Inject(Catalog) catalog: Catalog) {
    // Adapter to match v0.9 Catalog type which expects an id and components map
    // We pass a dummy catalog wrapper since the Angular renderer
    // doesn't use the core Catalog class for rendering resolution,
    // but the MessageProcessor needs it for validation/existence checks.
    //
    // TODO: This is a robust-enough hack for now, but we should align Types.
    super(
      [
        {
          id: 'default',
          components: new Map(),
          functions: BASIC_FUNCTIONS,
        } as any,
      ],
      (action) => {
        console.log('Action dispatched:', action);
      },
    );
  }
  readonly events = new Subject<DispatchedEvent>();

  // v0.8 A2uiMessageProcessor had getSurfaces, v0.9 does not (it has model.surfacesMap)
  // We re-implement it here for compatibility with the Angular template.
  getSurfaces(): ReadonlyMap<string, any> {
    return this.model.surfacesMap;
  }

  clearSurfaces() {
    this.model.dispose();
  }

  // Override to handle the fact that we're using a different base class
  // The base class processMessages expects v0.9 messages.
  // We trust the server sends valid v0.9 messages.
  override processMessages(messages: any[]): void {
    super.processMessages(messages);
  }

  dispatch(message: A2uiClientMessage): Promise<Types.A2uiMessage[]> {
    const completion = new Subject<Types.A2uiMessage[]>();
    this.events.next({ message, completion });
    return firstValueFrom(completion);
  }
}
