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

import { Component, input, computed, ChangeDetectionStrategy, inject, OnInit, DestroyRef, NgZone, Signal } from '@angular/core';
import { BoundProperty } from '../../core/types';
import { A2uiRendererService } from '../../core/a2ui-renderer.service';
import { ComponentContext } from '@a2ui/web_core/v0_9';
import { toAngularSignal } from '../../core/utils';

/**
 * Angular implementation of the A2UI TextField component (v0.9).
 *
 * Renders a text input field with an optional label and placeholder.
 * Updates the bound data model property on every input change.
 */
@Component({
  selector: 'a2ui-v09-text-field',
  standalone: true,
  imports: [],
  template: `
    <div class="a2ui-text-field-container">
      @if (label()) {
        <label>{{ label() }}</label>
      }
      <input
        [type]="inputType()"
        [value]="value()"
        (input)="handleInput($event)"
        [placeholder]="placeholder()"
        [class.invalid]="failedChecks().length > 0"
      />
      @for (check of failedChecks(); track check.message) {
        <div class="a2ui-error-message">{{ check.message }}</div>
      }
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
      input.invalid {
        border-color: red;
      }
      .a2ui-error-message {
        color: red;
        font-size: 12px;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TextFieldComponent implements OnInit {
  /**
   * Reactive properties resolved from the A2UI {@link ComponentModel}.
   *
   * Expected properties:
   * - `value`: The current string value of the input.
   * - `label`: Optional label text to display above the input.
   * - `placeholder`: Hint text shown when the input is empty.
   * - `variant`: Input type variant ('default', 'obscured' (password), 'number').
   * - `checks`: Optional validation rules.
   */
  props = input<Record<string, BoundProperty>>({});
  surfaceId = input.required<string>();
  componentId = input<string>();
  dataContextPath = input<string>('/');

  private rendererService = inject(A2uiRendererService);
  private destroyRef = inject(DestroyRef);
  private ngZone = inject(NgZone);

  resolvedChecks: { message: string; condition: Signal<boolean> }[] = [];

  label = computed(() => this.props()['label']?.value());
  value = computed(() => this.props()['value']?.value() || '');
  placeholder = computed(() => this.props()['placeholder']?.value() || '');
  variant = computed(() => this.props()['variant']?.value());

  ngOnInit() {
    const checksProp = this.props()['checks'];
    if (checksProp) {
      const checksArray = (checksProp.value() as any[]) || [];
      if (!this.rendererService.surfaceGroup) return;
      const surface = this.rendererService.surfaceGroup.getSurface(this.surfaceId());
      if (!surface) return;
      
      const context = new ComponentContext(surface, this.componentId() || '', this.dataContextPath());


      this.resolvedChecks = checksArray.map((check) => {
        const conditionSig = context.dataContext.resolveSignal(check.condition);
        const angSig = toAngularSignal(conditionSig as any, this.destroyRef, this.ngZone);
        return {
          message: check.message,
          condition: angSig as unknown as Signal<boolean>,
        };
      });
    }
  }

  failedChecks = computed(() => {
    return this.resolvedChecks.filter((check) => !check.condition());
  });

  inputType = computed(() => {
    switch (this.variant()) {
      case 'obscured':
        return 'password';
      case 'number':
        return 'number';
      default:
        return 'text';
    }
  });

  handleInput(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    // Update the data path.  If anything is listening to this path, it will be
    // notified.
    this.props()['value']?.onUpdate(value);
  }
}
