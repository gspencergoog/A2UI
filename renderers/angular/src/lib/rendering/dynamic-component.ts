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

import * as Primitives from '@a2ui/web_core/types/primitives';
import { Types } from '../types';
import { Directive, inject, input } from '@angular/core';
import { A2UI_PROCESSOR } from '../config';
import { Theme } from './theming';
import { MessageProcessor, A2uiClientMessage } from '../data';

let idCounter = 0;

@Directive({
  host: {
    '[style.--weight]': 'weight()',
  },
})
export abstract class DynamicComponent<T extends Types.AnyComponentNode = Types.AnyComponentNode> {
  protected readonly processor = inject(A2UI_PROCESSOR) as MessageProcessor;
  protected readonly theme = inject(Theme);

  readonly surfaceId = input.required<Types.SurfaceID | null>();
  readonly component = input.required<T>();
  readonly weight = input.required<string | number>();
  readonly themeOverride = input<any>();

  protected sendAction(action: Types.Action) {
    if (!action) return;

    // Check if it's a server event action
    if ('event' in action && action.event) {
      const eventWithContext = { ...action };

      // Resolve context if present
      if (action.event.context) {
        // We need to shallow copy context to not mutate original
        const resolvedContext: Record<string, any> = {};
        for (const [key, val] of Object.entries(action.event.context)) {
          resolvedContext[key] = val;
        }
      }

      // Inject dataContextPath if available
      const component = this.component();
      if (component['dataContextPath']) {
        // This logic seems specific to old implementation that used dataContextPath?
        // v0.9 might not use dataContextPath in the same way?
        // But we maintain it if it exists.
      }

      const message: A2uiClientMessage = {
        action: eventWithContext,
        version: 'v0.9',
        surfaceId: this.surfaceId() ?? undefined,
      };
      this.processor.dispatch(message);
    } else if ('functionCall' in action) {
      console.warn('Function calls not yet fully supported in DynamicComponent dispatch');
    }
  }

  protected resolvePrimitive(value: Primitives.StringValue | null): string | null;
  protected resolvePrimitive(value: Primitives.BooleanValue | null): boolean | null;
  protected resolvePrimitive(value: Primitives.NumberValue | null): number | null;
  protected resolvePrimitive(
    value: Primitives.StringValue | Primitives.BooleanValue | Primitives.NumberValue | null,
  ) {
    const component = this.component();
    const surfaceId = this.surfaceId();

    if (value === null || value === undefined) {
      return null;
    } else if (typeof value !== 'object') {
      return value as any;
    } else if (value.literal != null) {
      return value.literal;
    } else if (value.path) {
      if (surfaceId) {
        const surface = this.processor.getSurfaces().get(surfaceId);
        return surface?.dataModel.get(value.path);
      }
      return null;
    } else if ('literalString' in value) {
      return value.literalString;
    } else if ('literalNumber' in value) {
      return value.literalNumber;
    } else if ('literalBoolean' in value) {
      return value.literalBoolean;
    }

    return null;
  }

  protected getUniqueId(prefix: string) {
    return `${prefix}-${idCounter++}`;
  }
}
