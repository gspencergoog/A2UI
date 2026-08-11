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
   * Resolves the effective catalog ID following the strict 3-step fallback:
   * 1. Surface-specific catalog override
   * 2. Message-declared catalog
   * 3. Default catalog ID
   */
  resolveCatalogId(surfaceOverrideId?: string, messageDeclaredId?: string): string | undefined {
    if (surfaceOverrideId && this.catalogsMap.has(surfaceOverrideId)) {
      return surfaceOverrideId;
    }
    if (messageDeclaredId && this.catalogsMap.has(messageDeclaredId)) {
      return messageDeclaredId;
    }
    if (this.defaultCatalogId && this.catalogsMap.has(this.defaultCatalogId)) {
      return this.defaultCatalogId;
    }
    // Return first match if given, even if not pre-registered in map
    return surfaceOverrideId || messageDeclaredId || this.defaultCatalogId;
  }

  /**
   * Resolves the CatalogDefinition using the 3-step fallback.
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
