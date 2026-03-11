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

import { ChangeDetectionStrategy, Component, computed, input, effect, untracked, signal } from '@angular/core';
import { DataContext as WebCoreDataContext } from '@a2ui/web_core/v0_9';
import { Types } from '../types';
import { DynamicComponent } from '../rendering/dynamic-component';
import { Renderer } from '../rendering/renderer';

interface ChildListItem {
  componentId: string;
  context?: WebCoreDataContext;
}

@Component({
  selector: 'a2ui-list',
  imports: [Renderer],
  changeDetection: ChangeDetectionStrategy.Eager,
  host: {
    '[attr.direction]': 'direction()',
    '[attr.align]': 'align()',
  },
  styles: `
    :host {
      display: block;
      flex: var(--weight);
      min-height: 0;
    }

    :host([direction='vertical']) section {
      display: flex;
      flex-direction: column;
      max-height: 100%;
      overflow-y: auto;
    }

    :host([direction='horizontal']) section {
      display: flex;
      max-width: 100%;
      overflow-x: auto;
      overflow-y: hidden;
      scrollbar-width: none;
    }

    .a2ui-list-item {
      display: flex;
      cursor: pointer;
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
  `,
  template: `
    <section [class]="classes()" [style]="theme.additionalStyles?.List">
      @for (item of items(); track $index) {
        <div class="a2ui-list-item">
          <ng-container a2ui-renderer [surfaceId]="surfaceId()!" [component]="item.componentId" [dataContext]="item.context ?? null" />
        </div>
      }
    </section>
  `,
})
export class List extends DynamicComponent<Types.ListNode> {
  readonly direction = input<'vertical' | 'horizontal'>('vertical');
  readonly align = input<Types.ListNode['align']>('stretch');

  protected items = signal<ChildListItem[]>([]);

  constructor() {
    super();

    effect((onCleanup) => {
      const childrenProp = this.componentProperties()?.['children'];

      // Static Array Case
      if (Array.isArray(childrenProp)) {
        untracked(() => this.items.set(childrenProp.map(c => ({ componentId: c }))));
        return;
      }

      // Template Case
      if (childrenProp && typeof childrenProp === 'object' && 'componentId' in childrenProp && 'path' in childrenProp) {
        const context = untracked(() => this.getContext());
        if (!context) {
            untracked(() => this.items.set([]));
            return;
        }

        const sub = context.subscribeDynamicValue({ path: childrenProp.path }, (value: any) => {
          if (!Array.isArray(value)) {
            this.items.set([]);
            return;
          }

          const newItems = value.map((_, index) => {
             const itemPath = `${childrenProp.path}/${index}`;
             return {
               componentId: childrenProp.componentId,
               context: context.nested(itemPath)
             };
          });
          this.items.set(newItems);
        });

        if (Array.isArray(sub.value)) {
           const newItems = sub.value.map((_, index) => {
             const itemPath = `${childrenProp.path}/${index}`;
             return {
               componentId: childrenProp.componentId,
               context: context.nested(itemPath)
             };
          });
          untracked(() => this.items.set(newItems));
        } else {
          untracked(() => this.items.set([]));
        }

        onCleanup(() => sub.unsubscribe());
      }
    });
  }

  protected readonly classes = computed(() => ({
    ...this.theme.components.List,
    [`align-${this.align()}`]: true,
  }));
}
