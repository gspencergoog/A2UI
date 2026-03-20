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
import { DestroyRef } from '@angular/core';
import { ComponentContext, PreactReactiveProvider } from '@a2ui/web_core/v0_9';
import { ComponentBinder } from './component-binder.service';

describe('ComponentBinder', () => {
  let binder: ComponentBinder;
  let mockDestroyRef: jasmine.SpyObj<DestroyRef>;
  let onDestroyCallback: () => void;

  beforeEach(() => {
    onDestroyCallback = () => {};
    mockDestroyRef = jasmine.createSpyObj('DestroyRef', ['onDestroy']);
    mockDestroyRef.onDestroy.and.callFake((callback: () => void) => {
      onDestroyCallback = callback;
      return () => {}; // Return unregister function
    });

    TestBed.configureTestingModule({
      providers: [ComponentBinder, { provide: DestroyRef, useValue: mockDestroyRef }],
    });

    binder = TestBed.inject(ComponentBinder);
  });

  it('should be created', () => {
    expect(binder).toBeTruthy();
  });

  it('should bind properties to Angular signals', () => {
    const mockComponentModel = {
      properties: {
        text: 'Hello',
        visible: true,
      },
    };

    const provider = new PreactReactiveProvider();
    const mockDataContext = {
      resolveSignal: jasmine.createSpy('resolveSignal').and.callFake((val: any) => {
        // For test purposes, bindings resolve to 'initial'
        if (typeof val === 'object' && val?.path) return provider.toGenericSignal('initial');
        return provider.toGenericSignal(val);
      }),
      set: jasmine.createSpy('set'),
    };

    const mockContext = {
      componentModel: mockComponentModel,
      dataContext: mockDataContext,
    } as unknown as ComponentContext;

    const bound = binder.bind(mockContext);

    expect(bound['text']).toBeDefined();
    expect(bound['visible']).toBeDefined();
    expect(bound['text']()).toBe('Hello');
    expect(bound['visible']()).toBe(true);

    // Verify resolveSignal was called
    expect(mockDataContext.resolveSignal).toHaveBeenCalledWith('Hello');
    expect(mockDataContext.resolveSignal).toHaveBeenCalledWith(true);
  });

  it('should add update() method for data bindings (two-way binding)', () => {
    const mockComponentModel = {
      properties: {
        value: { path: '/data/text' },
      },
    };

    const provider = new PreactReactiveProvider();
    const mockDataContext = {
      resolveSignal: jasmine.createSpy('resolveSignal').and.callFake((val: any) => {
        // For test purposes, bindings resolve to 'initial'
        if (typeof val === 'object' && val?.path) return provider.toGenericSignal('initial');
        return provider.toGenericSignal(val);
      }),
      set: jasmine.createSpy('set'),
    };

    const mockContext = {
      componentModel: mockComponentModel,
      dataContext: mockDataContext,
    } as unknown as ComponentContext;

    const bound = binder.bind(mockContext);

    expect(bound['value']).toBeDefined();
    expect(bound['value']()).toBe('initial');
    expect(bound['value'].set).toBeDefined();

    // Call set
    bound['value'].set('new-value');

    // Verify set was called on DataContext
    expect(mockDataContext.set).toHaveBeenCalledWith('/data/text', 'new-value');
  });

  it('should NOT add update() method for literals', () => {
    const mockComponentModel = {
      properties: {
        text: 'Literal String',
      },
    };

    const provider = new PreactReactiveProvider();
    const mockDataContext = {
      resolveSignal: jasmine.createSpy('resolveSignal').and.callFake((val: any) => {
        // For test purposes, bindings resolve to 'initial'
        if (typeof val === 'object' && val?.path) return provider.toGenericSignal('initial');
        return provider.toGenericSignal(val);
      }),
      set: jasmine.createSpy('set'),
    };

    const mockContext = {
      componentModel: mockComponentModel,
      dataContext: mockDataContext,
    } as unknown as ComponentContext;

    const bound = binder.bind(mockContext);

    expect(bound['text']).toBeDefined();
    expect(bound['text']()).toBe('Literal String');
    expect(bound['text'].set).toBeDefined(); // No-op for literals

    // Call set on literal, should not crash or call set
    bound['text'].set('new');
    expect(mockDataContext.set).not.toHaveBeenCalled();
  });
});
