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
import { TextFieldApi, TextFieldApiType } from '@a2ui/web_core/v0_9/basic_catalog';

/**
 * Angular implementation of the A2UI TextField component (v0.9).
 */
@Component({
  selector: 'a2ui-v09-text-field',
  standalone: true,
  imports: [],
  template: `
    <div class="a2ui-text-field-container">
      @if (props().label) {
        <label>{{ props().label }}</label>
      }
      <input
        [type]="inputType"
        [value]="props().value || ''"
        (input)="handleInput($event)"
        [placeholder]="props().placeholder || ''"
      />
    </div>
  `,
  styles: [
    `
      :host {
        display: block;
        flex: 1;
        width: 100%;
      }
      .a2ui-text-field-container {
        display: flex;
        flex-direction: column;
        gap: 4px;
        margin: 4px;
      }
      input {
        padding: 8px;
        border: 1px solid #ccc;
        border-radius: 4px;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TextFieldComponent {
  /**
   * Reactive properties for the text field, resolved from the A2UI model.
   * Includes the current value, label, placeholder, and setters for data binding.
   */
  props = input.required<ResolveA2uiProps<TextFieldApiType>>();

  /**
   * Derived property for the HTML input type based on the component variant.
   */
  get inputType(): string {
    const variant = this.props().variant;
    switch (variant) {
      case 'obscured':
        return 'password';
      case 'number':
        return 'number';
      default:
        return 'text';
    }
  }

  /**
   * Handles user input and updates the underlying data model via the proxy setter.
   */
  handleInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.props().setValue?.(value);
  }
}
