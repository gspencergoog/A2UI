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

import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { Types } from '../types';
import { DynamicComponent } from '../rendering/dynamic-component';
import { Renderer } from '../rendering/renderer';
import * as Styles from '@a2ui/web_core/styles/index';

@Component({
  selector: 'a2ui-button',
  imports: [Renderer],
  changeDetection: ChangeDetectionStrategy.Eager,
  template: `
    <button
      [class]="classes()"
      [style]="additionalStyles()"
      (click)="handleClick()"
    >
      @if (component().properties.child; as child) {
        <ng-container a2ui-renderer [surfaceId]="surfaceId()!" [component]="child" [themeOverride]="childThemeOverride()" />
      }
    </button>
  `,
  styles: `
    :host {
      display: block;
      flex: var(--weight);
      min-height: 0;
    }
  `,
})
export class Button extends DynamicComponent<Types.ButtonNode> {
  readonly action = input.required<Types.Action | null>();
  readonly variant = input<string | null>();

  protected classes = computed(() => {
    const variant = this.variant();

    const buttonTheme = this.theme['components']?.Button;
    if (!buttonTheme) return {};

    if (typeof buttonTheme === 'string' || Array.isArray(buttonTheme)) {
        return buttonTheme;
    }

    let baseClasses = buttonTheme.all;
    if (baseClasses === undefined) {
      const isFlatMap = Object.values(buttonTheme).some(v => typeof v === 'boolean');
      if (isFlatMap) {
         baseClasses = buttonTheme;
      } else {
         baseClasses = {};
      }
    }

    return Styles.merge(
      baseClasses as Record<string, boolean>,
      variant ? (buttonTheme[variant] || {}) as Record<string, boolean> : {},
    );
  });

  protected additionalStyles = computed(() => {
    const variant = this.variant();
    const styles = this.theme['additionalStyles']?.Button;

    if (!styles) {
      return null;
    }

    if (variant && styles[variant]) {
        return styles[variant];
    }

    return styles;
  });

  protected childThemeOverride = computed(() => {
    const variant = this.variant();

    // Extracts Text and Icon styling definitions from the button theme to pass down to child components.
    const buttonTheme = this.theme['components']?.Button;
    if (!buttonTheme) return null;

    return {
        components: {
            Text: this.theme['components']?.ButtonText ? this.theme['components'].ButtonText[variant || 'all'] : null,
            Icon: this.theme['components']?.ButtonIcon ? this.theme['components'].ButtonIcon[variant || 'all'] : null,
        },
        additionalStyles: {
            Text: this.theme['additionalStyles']?.ButtonText ? this.theme['additionalStyles'].ButtonText[variant || 'all'] : null,
            Icon: this.theme['additionalStyles']?.ButtonIcon ? this.theme['additionalStyles'].ButtonIcon[variant || 'all'] : null,
        }
    };
  });

  protected handleClick() {
    const action = this.action();

    if (action) {
      super.sendAction(action);
    }
  }
}
