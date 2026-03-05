import { Observable } from 'rxjs';
import { DataModel } from '@a2ui/web_core/v0_9';

export interface DataContext {
  resolvePath(path: string): string;
  getValue(path: string): any;
  /**
   * Observes the value at the given path.
   * Returns an Observable that emits the current value and subsequent updates.
   */
  observe<T>(path: string): Observable<T>;
  nested(relativePath: string): DataContext;
}

export class DataContextImpl implements DataContext {
  constructor(
    private model: DataModel,
    private basePath: string = '/',
  ) {}

  resolvePath(path: string): string {
    if (path.startsWith('/')) {
      return path;
    }
    // Handle root base path specifically to avoid double slash
    const base = this.basePath === '/' ? '' : this.basePath;
    return `${base}/${path}`;
  }

  getValue(path: string): any {
    return this.model.get(this.resolvePath(path));
  }

  observe<T>(path: string): Observable<T> {
    const resolvedPath = this.resolvePath(path);
    return new Observable<T>((subscriber) => {
      // Emit initial value
      subscriber.next(this.model.get(resolvedPath));

      const subscription = this.model.subscribe<T>(resolvedPath, (value) => {
        if (value !== undefined) {
          subscriber.next(value);
        }
      });

      return () => {
        subscription.unsubscribe();
      };
    });
  }

  nested(relativePath: string): DataContext {
    return new DataContextImpl(this.model, this.resolvePath(relativePath));
  }
}
