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

import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { DynamicComponent } from '../rendering/dynamic-component';
import * as Primitives from '@a2ui/web_core/types/primitives';
import * as Styles from '@a2ui/web_core/styles/index';

@Component({
  selector: 'a2ui-icon',
  host: {
    'aria-hidden': 'true',
    tabindex: '-1',
  },
  changeDetection: ChangeDetectionStrategy.Eager,
  styles: `
    :host {
      display: block;
      flex: var(--weight);
      min-height: 0;
      overflow: auto;
    }
  `,
  template: `
    @let resolvedName = this.resolvedName();

    @if (resolvedName) {
      <section [class]="finalIconTheme()" [style]="finalIconStyles()">
        <span class="g-icon">{{ resolvedName }}</span>
      </section>
    }
  `,
})
export class Icon extends DynamicComponent {
  readonly name = input.required<Primitives.StringValue | null>();
  protected readonly resolvedName = computed(() => {
    const rawName = this.resolvePrimitive(this.name());
    if (!rawName) return null;
    // Material Symbols ligatures require snake_case.
    return rawName.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`).replace(/^_/, '');
  });

  protected overrideThemeStyles = computed(() => {
    const override = this.themeOverride();
    if (override && override.components && override.components.Icon) {
        return override.components.Icon;
    }
    return null;
  });

  protected overrideAdditionalStyles = computed(() => {
    const override = this.themeOverride();
    if (override && override.additionalStyles && override.additionalStyles.Icon) {
        return override.additionalStyles.Icon;
    }
    return null;
  });

  protected finalIconTheme = computed(() => {
      const base = this.theme.components?.Icon || {};
      const override = this.overrideThemeStyles();
      return override ? Styles.merge(base, override) : base;
  });

  protected finalIconStyles = computed(() => {
      const base = this.theme.additionalStyles?.Icon || {};
      const override = this.overrideAdditionalStyles();
      const merged = override ? { ...base, ...override } as Record<string, string> : base;
      return Object.keys(merged).length > 0 ? merged : null;
  });
}
