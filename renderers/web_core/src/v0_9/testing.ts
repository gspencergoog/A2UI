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

import { Catalog } from './catalog/types.js';
import { BASIC_COMPONENTS } from './basic_catalog/components/basic_components.js';
import { BASIC_FUNCTIONS } from './basic_catalog/functions/basic_functions.js';
import { PreactReactiveProvider } from './common/preact-provider.js';
import { ReactiveProvider } from './common/reactive.js';
import { DataContext } from './rendering/data-context.js';
import { SurfaceModel } from './state/surface-model.js';

/**
 * A standard catalog containing all basic A2UI components and functions.
 */
export const BasicCatalog = new Catalog('basic', BASIC_COMPONENTS, BASIC_FUNCTIONS);

/**
 * Creates a {@link DataContext} with a given {@link ReactiveProvider} (defaults to {@link PreactReactiveProvider}) for testing purposes.
 * 
 * @param provider Optional provider to use for the context.
 * @param surfaceId Optional ID for the surface.
 * @param basePath Optional base path in the data model.
 * @returns A fresh DataContext prepopulated with a reactive provider.
 */
export function createTestDataContext(provider?: ReactiveProvider, surfaceId = 'test_surface', basePath = '/') {
  const p = provider ?? new PreactReactiveProvider();
  const mockSurface = new SurfaceModel(surfaceId, BasicCatalog, p);
  return new DataContext(mockSurface, basePath);
}

export { PreactReactiveProvider as TestReactiveProvider };
