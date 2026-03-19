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
import { ButtonApi, ButtonApiType } from '@a2ui/web_core/v0_9/basic_catalog';
import { ChildComponent } from '../../core/child.component';

/**
 * Angular implementation of the A2UI Button component (v0.9).
 *
 * This component renders a clickable button that can dispatch an action
 * back to the agent. It supports primary and secondary variants and
 * can contain a single child component.
 */
@Component({
  selector: 'a2ui-v09-button',
  standalone: true,
  imports: [ChildComponent],
  template: `
    <button
      [type]="props().variant === 'primary' ? 'submit' : 'button'"
      [class]="'a2ui-button ' + (props().variant || 'default')"
      (click)="props().action?.()"
    >
      @if (props().child) {
        <a2ui-v09-child [meta]="props().child!" />
      }
    </button>
  `,
  styles: [
    `
      .a2ui-button {
        padding: 8px 16px;
        border-radius: 4px;
        border: 1px solid #ccc;
        cursor: pointer;
      }
      .a2ui-button.primary {
        background-color: #007bff;
        color: white;
        border-color: #0069d9;
      }
      .a2ui-button.borderless {
        background: none;
        border: none;
        padding: 0;
        color: #007bff;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ButtonComponent {
  /**
   * Reactive properties for the button, resolved from the A2UI model.
   * Includes the button variant, action handler, and optional child.
   */
  props = input.required<ResolveA2uiProps<ButtonApiType>>();
}

