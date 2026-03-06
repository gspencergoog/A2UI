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

import {
  Binding,
  ComponentRef,
  Directive,
  DOCUMENT,
  effect,
  inject,
  input,
  inputBinding,
  OnDestroy,
  PLATFORM_ID,
  Type,
  untracked,
  ViewContainerRef,
} from '@angular/core';
import * as Styles from '@a2ui/web_core/styles/index';
import * as Types from '@a2ui/web_core/types/types';
import { Catalog } from './catalog';
import { isPlatformBrowser } from '@angular/common';
import { A2UI_PROCESSOR } from '../config';

@Directive({
  selector: 'ng-container[a2ui-renderer]',
})
export class Renderer implements OnDestroy {
  private viewContainerRef = inject(ViewContainerRef);
  private catalog = inject(Catalog);

  private processor = inject(A2UI_PROCESSOR);
  private static hasInsertedStyles = false;

  private currentRef: ComponentRef<unknown> | null = null;
  private isDestroyed = false;

  readonly surfaceId = input.required<Types.SurfaceID>();
  readonly component = input.required<Types.AnyComponentNode | string>();
  readonly themeOverride = input<any>();

  constructor() {
    effect(() => {
      const surfaceId = this.surfaceId();
      const componentInput = this.component();
      const themeOverride = this.themeOverride();
      let component: Types.AnyComponentNode | undefined;

      if (typeof componentInput === 'string') {
        // Resolve ID to component node
        const surface = (this.processor as any).getSurfaces().get(surfaceId);
        if (surface && surface.componentsModel) {
          component = surface.componentsModel.get(componentInput);
        }
      } else {
        component = componentInput;
      }

      if (component) {
        untracked(() => this.render(surfaceId, component!, themeOverride));
      } else {
        untracked(() => this.clear());
      }
    });

    const platformId = inject(PLATFORM_ID);
    const document = inject(DOCUMENT);

    if (!Renderer.hasInsertedStyles && isPlatformBrowser(platformId)) {
      const styles = document.createElement('style');
      styles.textContent = Styles.structuralStyles;
      document.head.appendChild(styles);
      Renderer.hasInsertedStyles = true;
    }
  }

  ngOnDestroy(): void {
    this.isDestroyed = true;
    this.clear();
  }

  private async render(surfaceId: Types.SurfaceID, component: Types.AnyComponentNode, themeOverride?: any) {
    const config = this.catalog[component.type];
    let newComponent: Type<unknown> | null = null;
    let componentBindings: Binding[] | null = null;

    if (typeof config === 'function') {
      newComponent = await config();
    } else if (typeof config === 'object') {
      newComponent = await config.type();
      componentBindings = config.bindings(component as any);
    }

    this.clear();

    if (newComponent && !this.isDestroyed) {
      const bindings = [
        inputBinding('surfaceId', () => surfaceId),
        inputBinding('component', () => component),
        inputBinding('weight', () => component.weight ?? 'initial'),
      ];

      if (themeOverride) {
          bindings.push(inputBinding('themeOverride', () => themeOverride));
      }

      if (componentBindings) {
        bindings.push(...componentBindings);
      }

      this.currentRef = this.viewContainerRef.createComponent(newComponent, {
        bindings,
        injector: this.viewContainerRef.injector,
      });
    }
  }

  private clear() {
    this.currentRef?.destroy();
    this.currentRef = null;
  }
}
