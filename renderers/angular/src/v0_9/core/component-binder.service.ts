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

import { DestroyRef, Injectable, inject, NgZone, signal, Signal } from '@angular/core';
import { ComponentContext, GenericBinder } from '@a2ui/web_core/v0_9';
import { z } from 'zod';

/**
 * Service that binds A2UI ComponentModel properties to reactive Angular Signals.
 *
 * This service leverages the shared `@a2ui/web_core` `GenericBinder` to ensure
 * that property resolution and data binding logic is consistent across all
 * web-based renderers, while exposing the resulting properties as an
 * Angular-native {@link Signal}.
 */
@Injectable({
  providedIn: 'root',
})
export class ComponentBinder {
  private destroyRef = inject(DestroyRef);
  private ngZone = inject(NgZone);

  /**
   * Binds all properties of a component tree node to a single Angular Signal.
   *
   * The returned signal will automatically emit new values whenever the
   * underlying data model or component properties change. Updates are
   * automatically bridged into the Angular zone to ensure change detection
   * is triggered correctly.
   *
   * @param context The ComponentContext containing the model and data context.
   * @param schema The Zod schema defining the expected interface of the component.
   * @returns An object containing the Angular Signal as 'props' and a 'destroy'
   *          method to terminate the internal subscriptions.
   */
  bind<T>(
    context: ComponentContext,
    schema: z.ZodTypeAny,
  ): { props: Signal<T>; destroy: () => void } {
    const binder = new GenericBinder<T>(context, schema);

    // Create an Angular Signal initialized with the current binder snapshot
    const s = signal<T>(binder.snapshot);

    // Subscribe to binder updates and sync to the Angular signal
    const propsSub = binder.subscribe((props: T) => {
      console.log(`[ComponentBinder] Resolved props for ${context.componentModel.id}:`, props);
      // Ensure the signal update runs within the Angular zone to trigger change detection
      this.ngZone.run(() => s.set(props));
    });

    return {
      props: s.asReadonly(),
      destroy: () => propsSub.unsubscribe(),
    };
  }
}

