/**
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { DestroyRef, Injectable, inject, NgZone } from '@angular/core';
import { ComponentContext } from '@a2ui/web_core/v0_9';
import { computed } from '@preact/signals-core';
import { toAngularSignal } from './utils';
import { BoundProperty } from './types';

/**
 * Binds A2UI ComponentModel properties to reactive Angular Signals.
 *
 * This service is used by {@link ComponentHostComponent} to resolve data bindings
 * from the A2UI DataContext and expose them as Angular Signals. It ensures that
 * property updates from the A2UI protocol are correctly reflected in Angular
 * components and provides callbacks for updating the data model.
 */
@Injectable({
  providedIn: 'root',
})
export class ComponentBinder {
  private destroyRef = inject(DestroyRef);
  private ngZone = inject(NgZone);

  /**
   * Binds all properties of a component to an object of Angular Signals.
   *
   * @param context The ComponentContext containing the model and data context.
   * @returns An object where each key corresponds to a component prop and its value is an Angular Signal.
   */
  bind(context: ComponentContext): Record<string, BoundProperty> {
    const props = context.componentModel.properties;
    const bound: Record<string, any> = {};

    for (const key of Object.keys(props)) {
      const value = props[key];
      
      let preactSig;
      const isChildListTemplate = value && typeof value === 'object' && 'componentId' in value && 'path' in value;
      const isBoundPath = value && typeof value === 'object' && ('path' in value || 'call' in value) && !('componentId' in value);
      
      console.log('Binding prop', key, value, 'isBoundPath', isBoundPath);
      
      if (isChildListTemplate) {
        const listSig = context.dataContext.resolveSignal({ path: value.path });
        const listContext = context.dataContext.nested(value.path);
        preactSig = computed(() => {
          const arr = listSig.value;
          const currentArr = Array.isArray(arr) ? arr : [];
          return currentArr.map((_, i) => ({
            id: value.componentId,
            basePath: listContext.nested(String(i)).path,
          }));
        });
      } else {
        preactSig = context.dataContext.resolveSignal(value);
      }

      const angSig = toAngularSignal(preactSig as any, this.destroyRef, this.ngZone);

      bound[key] = {
        value: angSig,
        raw: value,
        onUpdate: isBoundPath
          ? (newValue: any) => {
              console.log('ComponentBinder onUpdate called', value.path, newValue);
              context.dataContext.set(value.path, newValue);
            }
          : () => {}, // No-op for non-bound values
      };
    }

    return bound;
  }
}
