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
import { ColumnApi, ColumnApiType } from '@a2ui/web_core/v0_9/basic_catalog';
import { ChildComponent } from '../../core/child.component';

/**
 * Angular implementation of the A2UI Column component (v0.9).
 */
@Component({
  selector: 'a2ui-v09-column',
  standalone: true,
  imports: [ChildComponent],
  template: `
    <div
      class="a2ui-column"
      [style.justify-content]="props().justify"
      [style.align-items]="props().align"
      style="display: flex; flex-direction: column; width: 100%;"
    >
      @for (child of props().children; track child.id) {
        <a2ui-v09-child [meta]="child" />
      }
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ColumnComponent {
  /**
   * Reactive properties for the column, resolved from the A2UI model.
   * Includes the list of children to render and layout alignment options.
   */
  props = input.required<ResolveA2uiProps<ColumnApiType>>();
}

