import { DataContext, DataContextImpl } from './data-context';
import { DataModel } from '@a2ui/web_core/v0_9';

import { Signal, signal } from '@angular/core';

class MockDataModel {
  private data = new Map<string, any>();
  subscriptions = new Map<string, any>();

  get(path: string): any {
    return this.data.get(path);
  }

  set(path: string, value: any): void {
    this.data.set(path, value);
  }

  // Minimal implementation for test
  update(path: string, value: any) {}
  delete(path: string) {}

  // Stubs for other methods
  subscribe(path: string) {
    return {} as any;
  }
  dispose() {}
  normalizePath(path: string) {
    return path;
  }

  // Add other required properties if any
}

describe('DataContext', () => {
  let model: MockDataModel;
  let rootContext: DataContext;

  beforeEach(() => {
    model = new MockDataModel();
    model.set('/foo', 'bar');
    model.set('/nested/val', 123);
    model.set('/list/0/name', 'Alice');

    rootContext = new DataContextImpl(model as unknown as DataModel, '/');
  });

  it('should resolve absolute paths correctly', () => {
    expect(rootContext.resolvePath('/foo')).toBe('/foo');
    expect(rootContext.resolvePath('/nested/val')).toBe('/nested/val');
  });

  it('should resolve values from absolute paths', () => {
    expect(rootContext.getValue('/foo')).toBe('bar');
  });

  describe('Nested Context', () => {
    it('should create a nested context with correct base path', () => {
      const child = rootContext.nested('nested');
      expect(child.resolvePath('val')).toBe('/nested/val');
    });

    it('should resolve absolute paths in nested context as absolute', () => {
      const child = rootContext.nested('nested');
      expect(child.resolvePath('/foo')).toBe('/foo');
    });

    it('should resolve relative paths against base path', () => {
      const listContext = rootContext.nested('list/0');
      expect(listContext.resolvePath('name')).toBe('/list/0/name');
    });

    it('should handle multiple levels of nesting', () => {
      const grandParent = new DataContextImpl(model as unknown as DataModel, '/a');
      const parent = grandParent.nested('b');
      const child = parent.nested('c');

      expect(child.resolvePath('d')).toBe('/a/b/c/d');
    });
  });
});
