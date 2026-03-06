import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Card } from './card';
import { Renderer } from '../rendering/renderer';
import { MessageProcessor } from '../data/processor';
import { Component, Input, Directive } from '@angular/core';
import { Types } from '../types';
import { Theme } from '../rendering/theming';
import { A2UI_PROCESSOR } from '../config';
import { By } from '@angular/platform-browser';
import { ComponentModel } from '@a2ui/web_core/v0_9';

// Mock Renderer to inspect inputs
@Directive({
  selector: 'ng-container[a2ui-renderer]',
  standalone: true,
})
class MockRenderer {
  @Input() surfaceId!: string;
  @Input() component!: string | Types.Component;
}

// Mock MessageProcessor
class MockMessageProcessor {
  getSurfaces() {
    return new Map([
      [
        'test-surface',
        {
          dataModel: {
            get: () => null,
          },
        },
      ],
    ]);
  }
}

const mockTheme = { components: {}, additionalStyles: {} };

describe('Card Component', () => {
  let fixture: ComponentFixture<Card>;
  let component: Card;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [Card, MockRenderer],
      providers: [
        { provide: MessageProcessor, useClass: MockMessageProcessor },
        { provide: A2UI_PROCESSOR, useClass: MockMessageProcessor },
        { provide: Theme, useValue: mockTheme },
      ],
    }).overrideComponent(Card, {
      remove: { imports: [Renderer] },
      add: {
        imports: [MockRenderer],
        providers: [{ provide: Theme, useValue: mockTheme }],
      },
    });

    fixture = TestBed.createComponent(Card);
    component = fixture.componentInstance;
  });

  it('should render children when passed a flat object (v0.8 style)', () => {
    fixture.componentRef.setInput('surfaceId', 'test-surface');
    fixture.componentRef.setInput('component', {
      id: 'card1',
      type: 'Card',
      properties: {
        children: ['child1', 'child2'],
      },
    } as any);
    fixture.componentRef.setInput('weight', '1');

    fixture.detectChanges();

    const renderers = fixture.debugElement.queryAllNodes(By.directive(MockRenderer));
    expect(renderers.length).toBe(2);
  });

  it('should render children when passed a ComponentModel (v0.9 style)', () => {
    const cardModel = new ComponentModel('card1', 'Card', {
      children: ['child1', 'child2'],
    });

    fixture.componentRef.setInput('surfaceId', 'test-surface');
    fixture.componentRef.setInput('component', cardModel as any);
    fixture.componentRef.setInput('weight', '1');

    fixture.detectChanges();

    const renderers = fixture.debugElement.queryAllNodes(By.directive(MockRenderer));
    expect(renderers.length).toBe(2);
  });
});
