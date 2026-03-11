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

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { List } from './list';
import { Renderer } from '../rendering/renderer';
import { MessageProcessor } from '../data/processor';
import { DataContext as WebCoreDataContext } from '@a2ui/web_core/v0_9';
import { Component, Input, Directive, inject } from '@angular/core';
import { Types } from '../types';
import { DynamicComponent } from '../rendering/dynamic-component';
import { Theme } from '../rendering/theming';
import { A2UI_PROCESSOR } from '../config';

import { CatalogToken } from '../rendering/catalog';
import { By } from '@angular/platform-browser';

// Mock Renderer to inspect inputs
@Directive({
  selector: 'ng-container[a2ui-renderer]',
  standalone: true,
})
class MockRenderer {
  @Input() surfaceId!: string;
  @Input() component!: string | Types.Component;
  @Input() dataContext?: WebCoreDataContext;
}

// Mock MessageProcessor
class MockMessageProcessor {
  getSurfaceSignal() {
    return () => ({
      componentsModel: new Map([
        ['item-template', { id: 'item-template', component: 'Text', text: 'Item' }],
      ]),
    });
  }
  getDataSignal() {
    return () => ({});
  }
  getDataModel(surfaceId: string) {
    return {
      get: (path: string) => {
        if (path === '/items') return ['A', 'B'];
        return null;
      },
    } as any;
  }
  sendAction() {}
}

const mockTheme = { components: {}, additionalStyles: {} };

describe('List Component', () => {
  let fixture: ComponentFixture<List>;
  let component: List;
  let context: WebCoreDataContext;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [List, MockRenderer],
      providers: [
        { provide: MessageProcessor, useClass: MockMessageProcessor },
        { provide: A2UI_PROCESSOR, useClass: MockMessageProcessor },
        { provide: Theme, useValue: mockTheme },
        { provide: CatalogToken, useValue: { id: 'test', entries: {}, functions: new Map() } as any },
      ],
    }).overrideComponent(List, {
      remove: { imports: [Renderer] },
      add: {
        imports: [MockRenderer],
        providers: [{ provide: Theme, useValue: mockTheme }],
      },
    });

    fixture = TestBed.createComponent(List);
    component = fixture.componentInstance;

    // Setup Context
    const model: any = {
      get: (path: string) => {
        if (path === '/items') return ['A', 'B'];
        return null;
      },
      subscribe: (path: string, cb: any) => {
        cb(['A', 'B']);
        return { unsubscribe: () => {} };
      }
    };
    context = new WebCoreDataContext(model, '/');

    // fixture.componentRef.setInput('dataContext', context);
    fixture.componentRef.setInput('surfaceId', 'test-surface');
    fixture.componentRef.setInput('component', {
      id: 'list1',
      type: 'List',
      properties: {
        children: [],
      },
    } as Types.ListNode);
    fixture.componentRef.setInput('weight', '1');

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render a static array of children components natively', async () => {
    fixture.componentRef.setInput('component', {
      id: 'list1',
      type: 'List',
      properties: {
        children: ['child1', 'child2'],
      },
    } as Types.ListNode);

    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const renderers = fixture.debugElement.queryAllNodes(By.directive(MockRenderer));
    expect(renderers.length).toBe(2);
    expect(renderers[0].injector.get(MockRenderer).component).toBe('child1');
    expect(renderers[1].injector.get(MockRenderer).component).toBe('child2');
  });

  it('should pass nested DataContext to children for template lists', async () => {
    fixture.componentRef.setInput('dataContext', context);
    fixture.componentRef.setInput('component', {
      id: 'list1',
      type: 'List',
      properties: {
        children: {
          componentId: 'item-template',
          path: '/items',
        },
      },
    } as Types.ListNode);

    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const renderers = fixture.debugElement.queryAllNodes(By.directive(MockRenderer));
    expect(renderers.length).toBe(2);

    const firstRenderer = renderers[0].injector.get(MockRenderer);
    expect(firstRenderer.component).toBe('item-template');
    expect(firstRenderer.dataContext?.path).toBe('/items/0');

    const secondRenderer = renderers[1].injector.get(MockRenderer);
    expect(secondRenderer.component).toBe('item-template');
    expect(secondRenderer.dataContext?.path).toBe('/items/1');
  });
});
