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

import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { ResolveA2uiProps } from '@a2ui/web_core/v0_9';
import { TextApi, TextApiType } from '@a2ui/web_core/v0_9/basic_catalog';

/**
 * Angular implementation of the A2UI Text component (v0.9).
 */
@Component({
  selector: 'a2ui-v09-text',
  standalone: true,
  imports: [],
  template: `
    <span
      [style.font-weight]="props().weight"
      [style.font-style]="props().style"
      [class]="'a2ui-text ' + (props().variant || 'body')"
    >
      {{ props().text }}
    </span>
  `,
  styles: [`
    .a2ui-text.h1 { font-size: 24px; font-weight: bold; }
    .a2ui-text.h2 { font-size: 20px; font-weight: bold; }
    .a2ui-text.h3 { font-size: 18px; font-weight: bold; }
    .a2ui-text.body { font-size: 16px; }
    .a2ui-text.caption { font-size: 12px; color: #666; }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TextComponent {
  /**
   * Reactive properties for the text component, resolved from the A2UI model.
   * Includes the text content, variant, weight, and style.
   */
  props = input.required<ResolveA2uiProps<TextApiType>>();
}

