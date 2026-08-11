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

/**
 * @fileoverview Strict 3-step Catalog Resolver for A2UI v1.0.
 *
 * Implements the 3-step catalog resolution fallback algorithm:
 * 1. Surface-specific catalog override
 * 2. Message-declared catalog
 * 3. Default catalog
 */

import {CatalogDefinition} from './catalog-definition.js';

export interface CatalogResolverOptions {
  /** Map of registered catalogs by catalogId */
  catalogs?: Map<string, CatalogDefinition> | Record<string, CatalogDefinition>;
  /** Default catalog ID to use as step 3 fallback */
  defaultCatalogId?: string;
}

export class CatalogResolver {
  private catalogsMap: Map<string, CatalogDefinition>;
  private defaultCatalogId?: string;

  constructor(options: CatalogResolverOptions = {}) {
    this.catalogsMap = new Map();
    if (options.catalogs) {
      if (options.catalogs instanceof Map) {
        options.catalogs.forEach((cat, id) => this.catalogsMap.set(id, cat));
      } else {
        Object.entries(options.catalogs).forEach(([id, cat]) => this.catalogsMap.set(id, cat));
      }
    }
    this.defaultCatalogId = options.defaultCatalogId;
  }

  /**
   * Registers or updates a catalog definition.
   */
  registerCatalog(catalog: CatalogDefinition): void {
    this.catalogsMap.set(catalog.catalogId, catalog);
  }

  /**
   * Returns whether a catalog ID is registered.
   */
  hasCatalog(catalogId: string): boolean {
    return this.catalogsMap.has(catalogId);
  }

  /**
   * Resolves the effective catalog ID following the strict 3-step fallback:
   * 1. Surface-specific catalog override (if provided)
   * 2. Message-declared catalog (if provided)
   * 3. Default catalog ID
   */
  resolveCatalogId(surfaceOverrideId?: string, messageDeclaredId?: string): string | undefined {
    if (surfaceOverrideId) {
      return surfaceOverrideId;
    }
    if (messageDeclaredId) {
      return messageDeclaredId;
    }
    return this.defaultCatalogId;
  }

  /**
   * Resolves the CatalogDefinition using the 3-step fallback.
   * Returns undefined if the resolved catalogId is not registered in the resolver.
   */
  resolveCatalog(
    surfaceOverrideId?: string,
    messageDeclaredId?: string,
  ): CatalogDefinition | undefined {
    const catalogId = this.resolveCatalogId(surfaceOverrideId, messageDeclaredId);
    if (!catalogId) {
      return undefined;
    }
    return this.catalogsMap.get(catalogId);
  }
}
