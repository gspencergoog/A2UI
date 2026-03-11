/*
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class IdGenerator {
  private counter = 0;

  /**
   * Generates a unique ID.
   *
   * @param prefix Optional prefix for the ID.
   */
  generate(prefix: string = 'id'): string {
    // In a real app, strict SSR hydration stability might require more complex handling
    // (e.g. using Angular's generic `useId` if available or provided via hydration).
    // For now, encapsulating slightly safer counter logic or UUIDs.
    // Using a simple counter per instance for now, but wrapped in a service
    // so it can be scoped or mocked.
    return `${prefix}-${this.counter++}`;
  }
}
