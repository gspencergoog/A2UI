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

import { TestBed, ComponentFixture } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { ComponentHostComponent, A2UI_SURFACE_ID, A2UI_DATA_CONTEXT_PATH } from './component-host.component';
import { A2uiRendererService } from './a2ui-renderer.service';
import { ComponentBinder } from './component-binder.service';
import { ComponentContext } from '@a2ui/web_core/v0_9';
import { Component, input, Signal, signal } from '@angular/core';
import { z } from 'zod';

@Component({
  selector: 'test-child',
  standalone: true,
  template: '<div>Child Component</div>',
})
class TestChildComponent {
  props = input.required<Signal<any>>();
}

describe('ComponentHostComponent', () => {
  let component: ComponentHostComponent;
  let fixture: ComponentFixture<ComponentHostComponent>;
  let mockRendererService: any;
  let mockCatalog: any;
  let mockBinder: jasmine.SpyObj<ComponentBinder>;
  let mockSurface: any;
  let mockSurfaceGroup: any;
  const testSchema = z.object({ text: z.string() });

  beforeEach(async () => {
    mockCatalog = {
      id: 'test-catalog',
      components: new Map([['TestType', { component: TestChildComponent, schema: testSchema }]]),
    };

    mockSurface = {
      componentsModel: new Map([
        ['comp1', { id: 'comp1', type: 'TestType', properties: { text: 'Hello' } }],
      ]),
      catalog: mockCatalog,
    };

    mockSurfaceGroup = {
      getSurface: jasmine.createSpy('getSurface').and.returnValue(mockSurface),
    };

    mockRendererService = {
      surfaceGroup: mockSurfaceGroup,
    };

    mockBinder = jasmine.createSpyObj('ComponentBinder', ['bind']);
    mockBinder.bind.and.returnValue({
      props: signal({ text: 'bound-hello' }),
      destroy: () => {},
    });

    await TestBed.configureTestingModule({
      imports: [ComponentHostComponent],
      providers: [
        { provide: A2uiRendererService, useValue: mockRendererService },
        { provide: ComponentBinder, useValue: mockBinder },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ComponentHostComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('componentId', 'comp1');
    fixture.componentRef.setInput('surfaceId', 'surf1');
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    it('should resolve component type and bind props with schema', () => {
      fixture.detectChanges(); // Triggers effect

      // Accessing protected properties via Signals
      // @ts-ignore
      expect(component.componentType()).toBe(TestChildComponent);
      // @ts-ignore
      expect(component.props()()).toEqual({ text: 'bound-hello' });

      expect(mockSurfaceGroup.getSurface).toHaveBeenCalledWith('surf1');
      expect(mockBinder.bind).toHaveBeenCalledWith(jasmine.any(ComponentContext), testSchema);

      const bindArg = mockBinder.bind.calls.mostRecent().args[0] as ComponentContext;
      expect(bindArg.componentModel.id).toBe('comp1');
      expect(bindArg.dataContext.path).toBe('/');
    });

    it('should provide A2UI paths via DI', async () => {
        fixture.detectChanges();
        const injector = fixture.debugElement.injector;
        expect(injector.get(A2UI_SURFACE_ID)).toBe('surf1');
        expect(injector.get(A2UI_DATA_CONTEXT_PATH)).toBe('/');
    });

    it('should warn and return if surface not found', () => {
      const consoleWarnSpy = spyOn(console, 'warn');
      mockSurfaceGroup.getSurface.and.returnValue(null);

      fixture.detectChanges();

      // @ts-ignore
      expect(component.componentType()).toBeNull();
      expect(consoleWarnSpy).toHaveBeenCalledWith('Surface surf1 not found');
    });

    it('should warn and return if component model not found', () => {
      const consoleWarnSpy = spyOn(console, 'warn');
      mockSurface.componentsModel.clear();

      fixture.detectChanges();

      // @ts-ignore
      expect(component.componentType()).toBeNull();
      expect(consoleWarnSpy).toHaveBeenCalledWith('Component comp1 not found in surface surf1');
    });

    it('should error and return if component type not in catalog', () => {
      const consoleErrorSpy = spyOn(console, 'error');
      mockCatalog.components.clear();

      fixture.detectChanges();

      // @ts-ignore
      expect(component.componentType()).toBeNull();
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Component type "TestType" not found in catalog "test-catalog"',
      );
    });
  });

  describe('Template rendering', () => {
    it('should render the resolved component', () => {
      fixture.detectChanges(); // Triggers ngOnInit and render

      const compiled = fixture.nativeElement;
      expect(compiled.innerHTML).toContain('Child Component');
    });
  });
});
