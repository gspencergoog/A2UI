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

import {
  ChangeDetectionStrategy,
  Component,
  Type,
  inject,
  input,
  Signal,
  effect,
  signal,
  InjectionToken,
} from '@angular/core';
import { NgComponentOutlet } from '@angular/common';
import { ComponentContext } from '@a2ui/web_core/v0_9';
import { A2uiRendererService } from './a2ui-renderer.service';
import { AngularCatalog } from '../catalog/types';
import { ComponentBinder } from './component-binder.service';

/** Injection token for the A2UI Surface ID. */
export const A2UI_SURFACE_ID = new InjectionToken<string>('A2UI_SURFACE_ID');

/** Injection token for the A2UI Data Context Path. */
export const A2UI_DATA_CONTEXT_PATH = new InjectionToken<string>('A2UI_DATA_CONTEXT_PATH');

/**
 * Host component for any A2UI component.
 *
 * This component is responsible for dynamically rendering an A2UI component
 * based on its `componentId`. It reactively manages the lifecycle of a
 * {@link ComponentContext} and uses the {@link ComponentBinder} to resolve
 * component properties (props) from the {@link DataModel}.
 *
 * It uses Angular's `NgComponentOutlet` to instantiate the appropriate
 * component type defined in the {@link AngularCatalog}.
 */
@Component({
  selector: 'a2ui-v09-component-host',
  imports: [NgComponentOutlet],
  providers: [
    {
      provide: A2UI_SURFACE_ID,
      useFactory: () => inject(ComponentHostComponent).surfaceId(),
    },
    {
      provide: A2UI_DATA_CONTEXT_PATH,
      useFactory: () => inject(ComponentHostComponent).dataContextPath(),
    },
  ],
  template: `
    @if (componentType()) {
      <ng-container
        *ngComponentOutlet="
          componentType();
          inputs: { props: props()?.() }
        "
      ></ng-container>
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ComponentHostComponent {
  /** The unique ID of the component to render within the surface. */
  componentId = input.required<string>();
  /** The ID of the surface this component belongs to. */
  surfaceId = input.required<string>();
  /**
   * The relative data context path for this component (e.g., within a list).
   * Defaults to root ('/').
   */
  dataContextPath = input<string>('/');

  private rendererService = inject(A2uiRendererService);
  private binder = inject(ComponentBinder);

  protected componentType = signal<Type<any> | null>(null);
  protected props = signal<Signal<any> | null>(null);

  constructor() {
    effect((onCleanup) => {
      const surfaceId = this.surfaceId();
      const componentId = this.componentId();
      const dataContextPath = this.dataContextPath();

      console.log(`[ComponentHost] Reacting to surface=${surfaceId}, component=${componentId}, path=${dataContextPath}`);

      const surface = this.rendererService.surfaceGroup?.getSurface(surfaceId);
      if (!surface) {
        console.warn(`Surface ${surfaceId} not found`);
        this.componentType.set(null);
        this.props.set(null);
        return;
      }

      const componentModel = surface.componentsModel.get(componentId);
      if (!componentModel) {
        console.warn(`Component ${componentId} not found in surface ${surfaceId}`);
        this.componentType.set(null);
        this.props.set(null);
        return;
      }

      const catalog = surface.catalog as AngularCatalog;
      const api = catalog.components.get(componentModel.type);
      if (!api) {
        console.error(
          `Component type "${componentModel.type}" not found in catalog "${catalog.id}"`,
        );
        this.componentType.set(null);
        this.props.set(null);
        return;
      }

      this.componentType.set(api.component);

      // Create context and bind properties using the component's schema
      const context = new ComponentContext(surface, componentId, dataContextPath);
      const binding = this.binder.bind<any>(context, api.schema);

      if (binding) {
        this.props.set(binding.props);

        // Clean up the binding when inputs changes or component is destroyed
        onCleanup(() => {
          binding.destroy?.();
        });
      }
    });
  }
}
