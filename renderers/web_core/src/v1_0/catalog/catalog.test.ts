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

import {describe, it} from 'node:test';
import assert from 'node:assert/strict';
import {CatalogDefinitionSchema} from './catalog-definition.js';
import {CatalogResolver} from './resolver.js';
import {validateComposition} from '../validating/composition.js';

describe('Catalog & Composition Tests (Phase 2)', () => {
  describe('CatalogDefinitionSchema (Map-based functions)', () => {
    it('parses valid catalog definition with map-based functions', () => {
      const catalogData = {
        protocolVersion: '1.0',
        catalogId: 'org.example.custom',
        title: 'Custom Catalog',
        components: {
          CustomButton: {
            allowedParents: ['Surface', 'Row', 'Column'],
          },
        },
        functions: {
          calculateTotal: {
            returnType: 'number',
            callableFrom: 'rendererOnly',
          },
        },
      };

      const parsed = CatalogDefinitionSchema.parse(catalogData);
      assert.equal(parsed.catalogId, 'org.example.custom');
      assert.equal(parsed.functions?.calculateTotal.returnType, 'number');
    });

    it('rejects component name Surface', () => {
      const catalogData = {
        catalogId: 'invalid',
        components: {
          Surface: {},
        },
      };

      assert.throws(() => CatalogDefinitionSchema.parse(catalogData));
    });

    it('rejects non-UAX31 function names', () => {
      const catalogData = {
        catalogId: 'invalid',
        functions: {
          'invalid-fn-name': {
            returnType: 'string',
          },
        },
      };

      assert.throws(() => CatalogDefinitionSchema.parse(catalogData));
    });
  });

  describe('CatalogResolver (Strict 3-step lookup & full coverage)', () => {
    const defaultCat = {catalogId: 'default-cat'};
    const msgCat = {catalogId: 'msg-cat'};
    const surfaceCat = {catalogId: 'surface-cat'};

    it('supports Map-based constructor and registerCatalog', () => {
      const catMap = new Map();
      catMap.set('default-cat', defaultCat);
      const resolver = new CatalogResolver({catalogs: catMap, defaultCatalogId: 'default-cat'});

      assert.equal(resolver.hasCatalog('default-cat'), true);
      assert.equal(resolver.hasCatalog('new-cat'), false);

      resolver.registerCatalog({catalogId: 'new-cat'});
      assert.equal(resolver.hasCatalog('new-cat'), true);
    });

    it('step 1: uses surface override when available', () => {
      const resolver = new CatalogResolver({
        catalogs: {'default-cat': defaultCat, 'msg-cat': msgCat, 'surface-cat': surfaceCat},
        defaultCatalogId: 'default-cat',
      });
      assert.equal(resolver.resolveCatalogId('surface-cat', 'msg-cat'), 'surface-cat');
      assert.equal(resolver.resolveCatalog('surface-cat', 'msg-cat'), surfaceCat);
    });

    it('step 2: falls back to message-declared catalog', () => {
      const resolver = new CatalogResolver({
        catalogs: {'default-cat': defaultCat, 'msg-cat': msgCat},
        defaultCatalogId: 'default-cat',
      });
      assert.equal(resolver.resolveCatalogId(undefined, 'msg-cat'), 'msg-cat');
      assert.equal(resolver.resolveCatalog(undefined, 'msg-cat'), msgCat);
    });

    it('step 3: falls back to default catalog', () => {
      const resolver = new CatalogResolver({
        catalogs: {'default-cat': defaultCat},
        defaultCatalogId: 'default-cat',
      });
      assert.equal(resolver.resolveCatalogId(undefined, undefined), 'default-cat');
      assert.equal(resolver.resolveCatalog(undefined, undefined), defaultCat);
    });

    it('returns undefined when resolved catalog is not registered in map', () => {
      const resolver = new CatalogResolver({
        catalogs: {'default-cat': defaultCat},
        defaultCatalogId: 'default-cat',
      });
      assert.equal(resolver.resolveCatalogId('unregistered-cat', undefined), 'unregistered-cat');
      assert.equal(resolver.resolveCatalog('unregistered-cat', undefined), undefined);
    });
  });

  describe('validateComposition (Edge Cases & Strict Parent/Child Rules)', () => {
    const catalog = {
      catalogId: 'test-cat',
      components: {
        Card: {
          allowedParents: ['Surface', 'Column'],
          allowedChildren: ['Text', 'Button'],
        },
        Text: {
          allowedParents: ['Card', 'Column'],
        },
        Button: {
          allowedParents: ['Card'],
        },
        Orphan: {
          allowedParents: [], // Empty array = ZERO allowed parents
        },
        LeafContainer: {
          allowedChildren: [], // Empty array = ZERO allowed children
        },
      },
    };

    it('validates surface root must be Surface', () => {
      const invalidComponents = [{id: 'root', type: 'Column'}];
      const errors = validateComposition(invalidComponents, 'root', catalog);
      assert.equal(errors.length, 1);
      assert.equal(errors[0].rule, 'surface_root');
    });

    it('enforces allowedParents = [] (disallows any parent)', () => {
      const comps = [
        {id: 'root', type: 'Surface', children: ['orphan1']},
        {id: 'orphan1', type: 'Orphan', parentId: 'root'},
      ];
      const errors = validateComposition(comps, 'root', catalog);
      assert.equal(errors.length, 1);
      assert.equal(errors[0].rule, 'allowed_parents');
    });

    it('enforces allowedChildren = [] (disallows any child)', () => {
      const comps = [
        {id: 'root', type: 'Surface', children: ['leaf1']},
        {id: 'leaf1', type: 'LeafContainer', parentId: 'root', children: ['text1']},
        {id: 'text1', type: 'Text', parentId: 'leaf1'},
      ];
      const errors = validateComposition(comps, 'root', catalog);
      assert.equal(errors.length, 2); // Triggers allowed_children on leaf1 AND allowed_parents on text1
    });

    it('reports dangling parent references', () => {
      const comps = [
        {id: 'root', type: 'Surface'},
        {id: 'text1', type: 'Text', parentId: 'non_existent_parent'},
      ];
      const errors = validateComposition(comps, 'root', catalog);
      assert.equal(errors.length, 1);
      assert.equal(errors[0].rule, 'allowed_parents');
    });

    it('reports dangling child references', () => {
      const comps = [
        {id: 'root', type: 'Surface', children: ['card1']},
        {id: 'card1', type: 'Card', parentId: 'root', children: ['non_existent_child']},
      ];
      const errors = validateComposition(comps, 'root', catalog);
      assert.equal(errors.length, 1);
      assert.equal(errors[0].rule, 'allowed_children');
    });
  });
});
