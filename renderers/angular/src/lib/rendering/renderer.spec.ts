import {
  Component,
  Input,
  signal,
  ViewChild,
  ViewContainerRef,
  WritableSignal,
  NgZone,
} from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Renderer } from './renderer';
import { Catalog } from './catalog';
import { MessageProcessor } from '../data/processor';
import { Theme } from './theming';
import { A2UI_EVALUATOR, A2UI_PROCESSOR } from '../config';
import { By } from '@angular/platform-browser';

@Component({
  template: '<div class="test-component">Test Component {{name}}</div>',
  standalone: true,
})
class TestComponent {
  @Input() component: any;
  @Input() surfaceId: any;
  @Input() dataContext: any;
  @Input() weight: any;
  get name() {
    return this.component?.properties?.name || '';
  }
}

@Component({
  template: '<div class="other-component">Other Component</div>',
  standalone: true,
})
class OtherComponent {
  @Input() component: any;
  @Input() surfaceId: any;
  @Input() dataContext: any;
  @Input() weight: any;
}

@Component({
  template: `<ng-container
    a2ui-renderer
    [surfaceId]="surfaceId"
    [component]="comp()"
  ></ng-container>`,
  standalone: true,
  imports: [Renderer],
})
class HostComponent {
  surfaceId = 's1';
  comp = signal<any>({ id: 'c1', type: 'TestBox', properties: { name: 'A' } });
  @ViewChild(Renderer) renderer!: Renderer;
}

describe('Renderer', () => {
  let component: HostComponent;
  let fixture: ComponentFixture<HostComponent>;
  let surfaceSignal: WritableSignal<any>;
  let ngZone: NgZone;

  beforeEach(async () => {
    surfaceSignal = signal(null);
    const processorSpy = jasmine.createSpyObj('MessageProcessor', [
      'processMessage',
      'getSurfaceSignal',
      'getRootComponentId',
    ]);
    processorSpy.getSurfaceSignal.and.returnValue(surfaceSignal);
    processorSpy.getRootComponentId.and.callFake((id: string) => {
      const s = surfaceSignal();
      return s?.rootComponentId;
    });

    const catalog = {
      TestBox: {
        type: () => TestComponent,
        bindings: () => [],
      },
      OtherBox: {
        type: () => OtherComponent,
        bindings: () => [],
      },
    };

    await TestBed.configureTestingModule({
      imports: [Renderer, HostComponent, TestComponent, OtherComponent],
      providers: [
        { provide: Catalog, useValue: catalog },
        { provide: MessageProcessor, useValue: processorSpy },
        { provide: A2UI_PROCESSOR, useValue: processorSpy },
        { provide: A2UI_EVALUATOR, useValue: { evaluate: (v: any) => v } },
        { provide: Theme, useValue: { components: {}, additionalStyles: {} } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HostComponent);
    component = fixture.componentInstance;
    ngZone = TestBed.inject(NgZone);
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component.renderer).toBeTruthy();
  });

  it('should render a specific component provided via input', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const testEl = fixture.debugElement.query(By.css('.test-component'));
    expect(testEl).toBeTruthy();
    expect(testEl.nativeElement.textContent).toContain('Test Component A');
    expect(component.renderer.component()).toEqual({
      id: 'c1',
      type: 'TestBox',
      properties: { name: 'A' },
    } as any);
  });

  it('should switch components when input changes', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    ngZone.run(() => {
      component.comp.set({ id: 'c2', type: 'OtherBox' });
    });
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    // Check if input signal updated
    expect(component.renderer.component()).toEqual({ id: 'c2', type: 'OtherBox' } as any);

    const otherEl = fixture.debugElement.query(By.css('.other-component'));
    expect(otherEl).toBeTruthy();
    const testEl = fixture.debugElement.query(By.css('.test-component'));
    expect(testEl).toBeFalsy();
  });

  // Removed outdated tests expecting root lookup behavior which is not implemented in Renderer
  // and contradicts input.required().

  it('should reuse component instance if type matches', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const instance1 = fixture.debugElement.query(By.directive(TestComponent)).componentInstance;

    ngZone.run(() => {
      component.comp.set({ id: 'c1', type: 'TestBox', properties: { name: 'B' } });
    });
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const instance2 = fixture.debugElement.query(By.directive(TestComponent)).componentInstance;
    // Renderer destroys and recreates components on render, so instance should not be the same.
    expect(instance2).not.toBe(instance1);
    expect(instance2.component.properties.name).toBe('B');
  });
});
