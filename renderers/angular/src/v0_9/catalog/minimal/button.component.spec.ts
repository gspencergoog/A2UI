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

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component, input, Signal, signal } from '@angular/core';
import { ButtonComponent } from './button.component';
import { A2uiRendererService } from '../../core/a2ui-renderer.service';
import { ComponentBinder } from '../../core/component-binder.service';
import { A2UI_SURFACE_ID } from '../../core/component-host.component';
import { By } from '@angular/platform-browser';

@Component({
  standalone: true,
  selector: 'dummy-child',
  template: 'Dummy Child',
})
class DummyChild {
  props = input.required<any>();
}

describe('ButtonComponent', () => {
  let component: ButtonComponent;
  let fixture: ComponentFixture<ButtonComponent>;
  let mockRendererService: any;
  let mockSurface: any;
  let mockSurfaceGroup: any;
  let mockBinder: any;

  beforeEach(async () => {
    mockSurface = {
      dispatchAction: jasmine.createSpy('dispatchAction'),
      componentsModel: new Map([
        ['child1', { id: 'child1', type: 'Text', properties: { text: 'Child Content' } }],
      ]),
      catalog: {
        id: 'test-catalog',
        components: new Map([
          [
            'Text',
            {
              component: DummyChild,
              schema: {}
            },
          ],
        ]),
      },
    };

    mockSurfaceGroup = {
      getSurface: jasmine.createSpy('getSurface').and.returnValue(mockSurface),
    };

    mockRendererService = {
      surfaceGroup: mockSurfaceGroup,
    };

    mockBinder = jasmine.createSpyObj('ComponentBinder', ['bind']);
    mockBinder.bind.and.returnValue({
      props: signal({}),
      destroy: () => {},
    });

    await TestBed.configureTestingModule({
      imports: [ButtonComponent],
      providers: [
        { provide: A2uiRendererService, useValue: mockRendererService },
        { provide: ComponentBinder, useValue: mockBinder },
        { provide: A2UI_SURFACE_ID, useValue: 'surf1' },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ButtonComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('props', {
      variant: 'primary',
      child: { id: 'child1', basePath: '/' },
      action: () => {},
    });
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should set button type to submit for primary variant', () => {
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('button'));
    expect(button.nativeElement.type).toBe('submit');
  });

  it('should set button type to button for non-primary variant', () => {
    fixture.componentRef.setInput('props', {
      variant: 'secondary',
      child: { id: 'child1', basePath: '/' },
      action: () => {},
    });
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('button'));
    expect(button.nativeElement.type).toBe('button');
  });

  it('should apply variant class', () => {
    fixture.detectChanges();
    const button = fixture.debugElement.query(By.css('button'));
    expect(button.nativeElement.classList).toContain('primary');
  });

  it('should handle click and call action from props', () => {
    const actionSpy = jasmine.createSpy('action');
    fixture.componentRef.setInput('props', {
      variant: 'primary',
      child: { id: 'child1', basePath: '/' },
      action: actionSpy,
    });
    fixture.detectChanges();
    
    const button = fixture.debugElement.query(By.css('button'));
    button.triggerEventHandler('click', null);

    expect(actionSpy).toHaveBeenCalled();
  });

  it('should show child component host if child prop is present', () => {
    fixture.detectChanges();
    const child = fixture.debugElement.query(By.css('a2ui-v09-child'));
    expect(child).toBeTruthy();
    expect(child.componentInstance.meta().id).toBe('child1');
  });

  it('should not show child component host if child prop is absent', () => {
    fixture.componentRef.setInput('props', {
      variant: 'primary',
      action: () => {},
    });
    fixture.detectChanges();
    const child = fixture.debugElement.query(By.css('a2ui-v09-child'));
    expect(child).toBeFalsy();
  });
});

