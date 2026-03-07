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
import { DynamicComponent } from '../rendering/dynamic-component';
import { Renderer } from '../rendering/renderer';
import { Types } from '../types';

@Component({
  selector: 'a2ui-row',
  imports: [Renderer],
  changeDetection: ChangeDetectionStrategy.Eager,
  host: {
    '[attr.align]': 'align()',
    '[attr.justify]': 'justify()',
  },
  styles: `
    :host {
      display: flex;
      flex: var(--weight);
    }

    section {
      display: flex;
      flex-direction: row;
      width: 100%;
      min-height: 100%;
      box-sizing: border-box;
    }

    .align-start {
      align-items: start;
    }

    .align-center {
      align-items: center;
    }

    .align-end {
      align-items: end;
    }

    .align-stretch {
      align-items: stretch;
    }

    .justify-start {
      justify-content: start;
    }

    .justify-center {
      justify-content: center;
    }

    .justify-end {
      justify-content: end;
    }

    .justify-spaceBetween {
      justify-content: space-between;
    }

    .justify-spaceAround {
      justify-content: space-around;
    }

    .justify-spaceEvenly {
      justify-content: space-evenly;
    }
  `,
  template: `
    <section [class]="classes()" [style]="theme.additionalStyles?.Row">
    <section [class]="classes()" [style]="theme.additionalStyles?.Row">
      @for (child of childrenArray(); track child) {
        <ng-container a2ui-renderer [surfaceId]="surfaceId()!" [component]="child" />
      }
    </section>
  `,
})
export class Row extends DynamicComponent<Types.RowNode> {
  readonly align = input<Types.RowNode['align']>('start');
  readonly justify = input<Types.RowNode['justify']>('start');

  protected readonly childrenArray = computed(() => {
    const children = this.component().properties.children;
    if (Array.isArray(children)) {
      return children;
    }
    // Handle the { path: string, componentId: string } case
    // This requires processor context which may need a different approach
    return []; // Fallback for now, usually handled by a higher-order component or specific rendering logic
  });

  protected readonly classes = computed(() => ({
    ...this.theme.components.Row,
    [`align-${this.align()}`]: true,
    [`justify-${this.justify()}`]: true,
  }));
}
