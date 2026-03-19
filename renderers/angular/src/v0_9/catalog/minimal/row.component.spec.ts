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
import { RowComponent } from './row.component';
import { A2uiRendererService } from '../../core/a2ui-renderer.service';
import { ComponentBinder } from '../../core/component-binder.service';
import { A2UI_SURFACE_ID } from '../../core/component-host.component';
import { By } from '@angular/platform-browser';
import { of } from 'rxjs';

@Component({
  standalone: true,
  selector: 'dummy-child',
  template: 'Dummy Child',
})
class DummyChild {
  props = input.required<any>();
}

describe('RowComponent', () => {
  let component: RowComponent;
  let fixture: ComponentFixture<RowComponent>;
  let mockRendererService: any;
  let mockSurface: any;
  let mockSurfaceGroup: any;
  let mockBinder: any;

  beforeEach(async () => {
    const mockContext = {
      componentModel: {
        id: 'test-component',
        type: 'TextField',
        properties: { text: 'Initial' },
        onUpdated: of(null),
      },
      dataContext: { path: '/', get: (path: string) => null },
    };

    mockSurface = {
      componentsModel: new Map([
        ['child1', { id: 'child1', type: 'Child', properties: {} }],
        ['child2', { id: 'child2', type: 'Child', properties: {} }],
      ]),
      catalog: {
        id: 'test-catalog',
        components: new Map([['Child', { component: DummyChild, schema: {} }]]),
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
      imports: [RowComponent],
      providers: [
        { provide: A2uiRendererService, useValue: mockRendererService },
        { provide: ComponentBinder, useValue: mockBinder },
        { provide: A2UI_SURFACE_ID, useValue: 'surf1' },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(RowComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('props', {
      justify: 'center',
      align: 'baseline',
      children: [
        { id: 'child1', basePath: '/' },
        { id: 'child2', basePath: '/' },
      ],
    });
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should apply flex styles from props', () => {
    fixture.detectChanges();
    const div = fixture.debugElement.query(By.css('.a2ui-row'));
    expect(div.styles['justify-content']).toBe('center');
    expect(div.styles['align-items']).toBe('baseline');
  });

  it('should render children using a2ui-v09-child', () => {
    fixture.detectChanges();
    const children = fixture.debugElement.queryAll(By.css('a2ui-v09-child'));
    expect(children.length).toBe(2);
    expect(children[0].componentInstance.meta().id).toBe('child1');
    expect(children[1].componentInstance.meta().id).toBe('child2');
  });
});
