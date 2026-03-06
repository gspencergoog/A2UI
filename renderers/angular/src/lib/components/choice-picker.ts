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

import { ChangeDetectionStrategy, Component, computed } from '@angular/core';
import { Types } from '../types';
import { DynamicComponent } from '../rendering/dynamic-component';
import { Renderer } from '../rendering/renderer';

interface Option {
  label: string;
  value: string;
}

@Component({
  selector: 'a2ui-choice-picker',
  template: `
    @let label = this.resolvedLabel();
    @let opts = this.resolvedOptions();

    <section
      [class]="
        theme.components.ChoicePicker?.container || theme.components.MultipleChoice?.container
      "
    >
      @if (label) {
        <label
          [class]="theme.components.ChoicePicker?.label || theme.components.MultipleChoice?.label"
          [for]="selectId"
          >{{ label }}</label
        >
      }

      <select
        (change)="handleChange($event)"
        [id]="selectId"
        [value]="resolvedValue()"
        [class]="theme.components.ChoicePicker?.element || theme.components.MultipleChoice?.element"
        [style]="theme.additionalStyles?.ChoicePicker"
      >
        @for (option of opts; track option.value) {
          <option [value]="option.value">{{ option.label }}</option>
        }
      </select>
    </section>
  `,
  styles: `
    :host {
      display: block;
      flex: var(--weight);
      min-height: 0;
      overflow: auto;
    }

    select {
      width: 100%;
      box-sizing: border-box;
    }
  `,
})
export class ChoicePicker extends DynamicComponent<Types.ChoicePicker> {
  protected readonly selectId = this.getUniqueId('a2ui-choice-picker');

  protected resolvedValue = computed(() => {
    const val = this.component().properties.value;
    if (typeof val === 'string' && val.startsWith('/')) {
      const surfaceId = this.surfaceId();
      if (surfaceId) {
        const surface = this.processor.model.getSurface(surfaceId);
        const dataPath = this.processor.resolvePath(
          val,
          (this.component() as any)['dataContextPath'],
        );
        return surface?.dataModel.get(dataPath) as string;
      }
    }
    return val as string;
  });

  protected resolvedLabel = computed(() => this.component().properties.label);

  protected resolvedOptions = computed(() => {
    const opts = this.component().properties.options;
    const surfaceId = this.surfaceId();
    const surface = surfaceId ? this.processor.model.getSurface(surfaceId) : undefined;

    if (typeof opts === 'string') {
      // Legacy or simplified path
      if (surface) {
        const dataPath = this.processor.resolvePath(
          opts,
          (this.component() as any)['dataContextPath'],
        );
        return (surface.dataModel.get(dataPath) as Option[]) || [];
      }
      return [];
    }
    if (opts && typeof opts === 'object' && !Array.isArray(opts) && 'path' in opts) {
      // DynamicList with path
      if (surface) {
        const path = (opts as { path: string }).path;
        const dataPath = this.processor.resolvePath(
          path,
          (this.component() as any)['dataContextPath'],
        );
        return (surface.dataModel.get(dataPath) as Option[]) || [];
      }
      return [];
    }
    return opts as Option[];
  });

  protected handleChange(event: Event) {
    const rawValue = this.component().properties.value;
    // Only update if it is a path
    if (typeof rawValue !== 'string' || !rawValue.startsWith('/')) {
      return;
    }

    const target = event.target as HTMLSelectElement;
    if (!target) {
      return;
    }

    const surfaceId = this.surfaceId();
    if (surfaceId) {
      const surface = this.processor.model.getSurface(surfaceId);
      const dataPath = this.processor.resolvePath(
        rawValue,
        (this.component() as any)['dataContextPath'],
      );
      surface?.dataModel.set(dataPath, target.value);
    }
  }
}
