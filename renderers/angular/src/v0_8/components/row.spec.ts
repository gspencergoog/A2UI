import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Row } from './row';
import { MessageProcessor } from '../data/processor';
import { Theme } from '../rendering/theming';
import { Catalog } from '../rendering/catalog';
import { Renderer } from '../rendering/renderer';
import { Types } from '../types';
import { Component, Directive, Input, ChangeDetectionStrategy } from '@angular/core';
import { By } from '@angular/platform-browser';

@Directive({
  selector: '[a2ui-renderer]',
  standalone: true,
})
class MockRenderer {
  @Input() surfaceId!: string;
  @Input() component!: any;

  static instances: MockRenderer[] = [];
  constructor() {
    MockRenderer.instances.push(this);
  }
}

describe('Row Component', () => {
  let component: Row;
  let fixture: ComponentFixture<Row>;
  let mockTheme: Theme;

  const mockNode: Types.RowNode = {
    id: 'row-1',
    type: 'Row',
    weight: 1,
    properties: {
      children: [{ id: 'child-1', type: 'Text', properties: {} }],
    },
  };

  beforeEach(async () => {
    mockTheme = new Theme();
    mockTheme.components = { Row: { 'custom-row': true } } as any;

    await TestBed.configureTestingModule({
      imports: [Row],
      providers: [
        { provide: MessageProcessor, useValue: {} },
        { provide: Theme, useValue: mockTheme },
        { provide: Catalog, useValue: {} },
      ],
    })
    .overrideComponent(Row, {
      set: {
        changeDetection: ChangeDetectionStrategy.Default,
        imports: [MockRenderer],
      }
    })
    .compileComponents();

    MockRenderer.instances = []; // Clear tracking

    fixture = TestBed.createComponent(Row);
    component = fixture.componentInstance;
    
    fixture.componentRef.setInput('surfaceId', 'surface-1');
    fixture.componentRef.setInput('component', mockNode);
    fixture.componentRef.setInput('weight', 1);

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should apply alignment and distribution classes', () => {
    const sectionEl = fixture.nativeElement.querySelector('section');
    expect(sectionEl.className).toContain('align-stretch'); // Default
    expect(sectionEl.className).toContain('distribute-start'); // Default

    fixture.componentRef.setInput('alignment', 'center');
    fixture.componentRef.setInput('distribution', 'end');
    fixture.detectChanges();

    expect(sectionEl.className).toContain('align-center');
    expect(sectionEl.className).toContain('distribute-end');
  });

  it('should render child components', () => {
    expect(MockRenderer.instances.length).toBe(1);
  });
});
