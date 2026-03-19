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

import { Type } from '@angular/core';
import { Catalog, ComponentApi } from '@a2ui/web_core/v0_9';

/**
 * Defines the interface for an Angular component mapped to an A2UI type.
 *
 * This interface extends the platform-agnostic `ComponentApi` by adding
 * required metadata for the Angular renderer, such as the actual
 * component class via the `component` property.
 */
export interface AngularComponentApi extends ComponentApi {
  /**
   * The Angular component class (decorated with `@Component`)
   * used to render this component type.
   */
  readonly component: Type<any>;
}

/**
 * A collection of component definitions supported by the Angular renderer.
 *
 * Catalogs map string identifiers (e.g., 'button', 'text') to their corresponding
 * implementations and API schemas.
 */
export class AngularCatalog extends Catalog<AngularComponentApi> {}
