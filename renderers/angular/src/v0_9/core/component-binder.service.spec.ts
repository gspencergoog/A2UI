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

import { TestBed } from '@angular/core/testing';
import { ComponentBinder } from './component-binder.service';
import { A2uiRendererService } from './a2ui-renderer.service';
import { of, Subject } from 'rxjs';
import { z } from 'zod';
import { ActionSchema, DataBindingSchema } from '@a2ui/web_core/v0_9';

describe('ComponentBinder', () => {
  let service: ComponentBinder;
  let mockRendererService: any;
  let mockSurface: any;
  let mockSurfaceGroup: any;

  // Define a schema that GenericBinder recognizes as having dynamic data and actions
  const testSchema = z.object({
    text: z.union([z.string(), DataBindingSchema]).optional(),
    visible: z.boolean().optional(),
    action: ActionSchema.optional(),
  });

  beforeEach(() => {
    mockSurface = {
      dispatchAction: jasmine.createSpy('dispatchAction'),
    };

    mockSurfaceGroup = {
      getSurface: jasmine.createSpy('getSurface').and.returnValue(mockSurface),
    };

    mockRendererService = {
      surfaceGroup: mockSurfaceGroup,
    };

    TestBed.configureTestingModule({
      providers: [
        ComponentBinder,
        { provide: A2uiRendererService, useValue: mockRendererService },
      ],
    });
    service = TestBed.inject(ComponentBinder);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  function createMockContext(properties: any, onUpdated: any = of(null)) {
    return {
      componentModel: {
        id: 'test-component',
        type: 'Test',
        properties,
        onUpdated: onUpdated,
      },
      dataContext: {
        path: '/',
        get: jasmine.createSpy('get').and.returnValue(null),
        subscribeDynamicValue: jasmine.createSpy('subscribeDynamicValue').and.callFake((val: any, cb: any) => {
          return { value: val?.path ? 'resolved-value' : val, unsubscribe: () => {} };
        }),
        resolveDynamicValue: jasmine.createSpy('resolveDynamicValue').and.callFake((val: any) => {
           return val?.path ? 'resolved-value' : val;
        }),
      },
      dispatchAction: jasmine.createSpy('dispatchAction'),
    };
  }

  it('should bind properties to a single Angular signal', () => {
    const mockContext = createMockContext({ text: 'Initial' });
    const { props } = service.bind<any>(mockContext as any, testSchema);
    expect(props()).toBeDefined();
    expect(props().text).toBe('Initial');
  });

  it('should include setters directly on the props for dynamic properties', () => {
    const mockContext = createMockContext({ text: { path: 'user.name' } });
    const { props } = service.bind<any>(mockContext as any, testSchema);
    expect(props().setText).toBeDefined();
    expect(typeof props().setText).toBe('function');
  });

  it('should handle actions by wrapping them in a function', () => {
    const mockContext = createMockContext({
      action: { event: { name: 'test-event' } },
    });

    const { props } = service.bind<any>(mockContext as any, testSchema);
    expect(typeof props().action).toBe('function');

    props().action();
    expect(mockContext.dispatchAction).toHaveBeenCalled();
  });

  it('should update the signal when the model changes', () => {
    let properties = { text: 'Initial' };
    const onUpdated = new Subject<void>();
    const mockContext = createMockContext(properties, onUpdated.asObservable());

    // Override properties getter to be dynamic for this test
    Object.defineProperty(mockContext.componentModel, 'properties', {
      get: () => properties,
    });

    const { props } = service.bind<any>(mockContext as any, testSchema);
    expect(props().text).toBe('Initial');

    // Simulate model update
    properties = { text: 'Reactive Update' };
    onUpdated.next();

    expect(props().text).toBe('Reactive Update');
  });

  it('should stop updating after destroy is called', () => {
    let properties = { text: 'Initial' };
    const onUpdated = new Subject<void>();
    const mockContext = createMockContext(properties, onUpdated.asObservable());

    Object.defineProperty(mockContext.componentModel, 'properties', {
      get: () => properties,
    });

    const { props, destroy } = service.bind<any>(mockContext as any, testSchema);
    expect(props().text).toBe('Initial');

    destroy();

    // Simulate model update after destroy
    properties = { text: 'Update after destroy' };
    onUpdated.next();

    // Value should NOT have updated if destruction was successful
    expect(props().text).not.toBe('Update after destroy');
    expect(props().text).toBe('Initial');
  });
});
