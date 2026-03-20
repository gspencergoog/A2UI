/**
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the \"License\");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an \"AS IS\" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { Injector } from '@angular/core';
import { createTestDataContext as createBaseContext } from '@a2ui/web_core/v0_9';
import { AngularReactiveProvider } from './core/angular-reactive-provider';

/**
 * Creates a DataContext populated with an AngularReactiveProvider.
 * Useful for testing Angular components or services that require native signals.
 * 
 * @param injector The Angular Injector to use for the reactive provider.
 * @param surfaceId Optional ID for the surface.
 * @param basePath Optional base path in the data model.
 * @returns A DataContext configured with Angular native signals.
 */
export function createAngularTestDataContext(
  injector: Injector,
  surfaceId?: string,
  basePath?: string
) {
  return createBaseContext(new AngularReactiveProvider(injector), surfaceId, basePath);
}
