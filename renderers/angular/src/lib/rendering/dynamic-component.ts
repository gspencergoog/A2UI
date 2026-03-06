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
import { DataContext as WebCoreDataContext } from '@a2ui/web_core/v0_9';
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
    const surfaceId = this.surfaceId();
    if (!surfaceId) {
      console.warn('Cannot dispatch action: No surface ID available.');
      return;
    }

    const surface = this.processor.getSurfaces().get(surfaceId);
    const catalog = surface?.catalog;

    const funcInvoker = (name: string, args: Record<string, any>, ctx: WebCoreDataContext) => {
      const func = catalog?.functions?.get(name);
      if (!func) throw new Error(`Function ${name} not found`);
      return func(args, ctx);
    };

    const context = surface ? new WebCoreDataContext(surface.dataModel, '/', funcInvoker) : null;

    if ('event' in action && action.event) {
      // Resolve context if present
      const resolvedContext: Record<string, any> = {};
      if (action.event.context) {
        for (const [key, val] of Object.entries(action.event.context)) {
          resolvedContext[key] = this.snapshotDynamicValue(context, val as any);
        }
      }

      const message: A2uiClientMessage = {
        version: 'v0.9',
        action: {
          name: action.event.name,
          surfaceId: surfaceId,
          sourceComponentId: this.component().id,
          timestamp: new Date().toISOString(),
          context: resolvedContext,
        },
      };

      this.processor.dispatch(message);
    } else if ('functionCall' in action && action.functionCall) {
      const funcName = action.functionCall.call;

      if (catalog && catalog.functions && !catalog.functions.has(funcName)) {
        const errorMsg: A2uiClientMessage = {
          version: 'v0.9',
          error: {
            code: 'FUNCTION_NOT_FOUND',
            message: `Action attempted to call unregistered function '${funcName}'. Expected one of: ${Array.from(catalog.functions.keys()).join(', ')}`,
            surfaceId: surfaceId,
          },
        };
        this.processor.dispatch(errorMsg);
        return; // Halt execution
      }

      // We have the function, lets execute it locally!
      const resolvedArgs: Record<string, any> = {};
      if (action.functionCall.args) {
        for (const [key, val] of Object.entries(action.functionCall.args)) {
          resolvedArgs[key] = this.snapshotDynamicValue(context, val as any);
        }
      }

      const func = catalog?.functions?.get(funcName);
      if (func) {
        try {
          func(resolvedArgs, context);
        } catch (e: any) {
          const errorMsg: A2uiClientMessage = {
            version: 'v0.9',
            error: {
              code: 'FUNCTION_EXECUTION_FAILED',
              message: `Function '${funcName}' failed: ${e.message || String(e)}`,
              surfaceId: surfaceId,
            },
          };
          this.processor.dispatch(errorMsg);
        }
      }
    }
  }

  private snapshotDynamicValue(context: WebCoreDataContext | null, val: any): any {
    if (!context) {
      return this.resolvePrimitive(val);
    }
    const sub = context.subscribeDynamicValue(val, () => {});
    const value = sub.value;
    sub.unsubscribe();
    return value;
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
