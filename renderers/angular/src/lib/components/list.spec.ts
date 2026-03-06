import { ComponentFixture, TestBed } from '@angular/core/testing';
import { List } from './list';
import { Renderer } from '../rendering/renderer';
import { MessageProcessor } from '../data/processor';
import { DataContext, DataContextImpl } from '../data/data-context';
import { Component, Input, Directive, inject } from '@angular/core';
import { Types } from '../types';
import { DynamicComponent } from '../rendering/dynamic-component';
import { Theme } from '../rendering/theming';
import { A2UI_PROCESSOR } from '../config';
import { By } from '@angular/platform-browser';

// Mock Renderer to inspect inputs
@Directive({
  selector: 'ng-container[a2ui-renderer]',
  standalone: true,
})
class MockRenderer {
  @Input() surfaceId!: string;
  @Input() component!: string | Types.Component;
  @Input() dataContext?: DataContext;
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
  let context: DataContext;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [List, MockRenderer],
      providers: [
        { provide: MessageProcessor, useClass: MockMessageProcessor },
        { provide: A2UI_PROCESSOR, useClass: MockMessageProcessor },
        { provide: Theme, useValue: mockTheme },
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
    };
    context = new DataContextImpl(model, '/');

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

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  /*
  it('should pass nested DataContext to children for template lists', () => {
    const renderers = fixture.debugElement.queryAllNodes(By.directive(MockRenderer));
    expect(renderers.length).toBe(2);

    const firstRenderer = renderers[0].injector.get(MockRenderer);
    expect(firstRenderer.dataContext).toBeDefined();
    expect(firstRenderer.dataContext).not.toBe(context);

    // Additional Verification: Check path
    // Since we mocked DataContextImpl to return paths as is for inspection, we can cast and check if possible.
    // But DataContextImpl is private implementation details usually.
    // However, we rely on behavior.
  });
  */
});
