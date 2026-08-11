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

  describe('CatalogResolver (Strict 3-step lookup)', () => {
    const defaultCat = {catalogId: 'default-cat'};
    const msgCat = {catalogId: 'msg-cat'};
    const surfaceCat = {catalogId: 'surface-cat'};

    const resolver = new CatalogResolver({
      catalogs: {
        'default-cat': defaultCat,
        'msg-cat': msgCat,
        'surface-cat': surfaceCat,
      },
      defaultCatalogId: 'default-cat',
    });

    it('step 1: uses surface override when available', () => {
      const resolved = resolver.resolveCatalogId('surface-cat', 'msg-cat');
      assert.equal(resolved, 'surface-cat');
    });

    it('step 2: falls back to message-declared catalog', () => {
      const resolved = resolver.resolveCatalogId(undefined, 'msg-cat');
      assert.equal(resolved, 'msg-cat');
    });

    it('step 3: falls back to default catalog', () => {
      const resolved = resolver.resolveCatalogId(undefined, undefined);
      assert.equal(resolved, 'default-cat');
    });
  });

  describe('validateComposition (Surface root & parent/child rules)', () => {
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
      },
    };

    it('validates surface root must be Surface', () => {
      const invalidComponents = [{id: 'root', type: 'Column'}];
      const errors = validateComposition(invalidComponents, 'root', catalog);
      assert.equal(errors.length, 1);
      assert.equal(errors[0].rule, 'surface_root');
    });

    it('passes for valid surface root Surface', () => {
      const validComponents = [
        {id: 'root', type: 'Surface', children: ['card1']},
        {id: 'card1', type: 'Card', parentId: 'root', children: ['text1']},
        {id: 'text1', type: 'Text', parentId: 'card1'},
      ];
      const errors = validateComposition(validComponents, 'root', catalog);
      assert.equal(errors.length, 0);
    });

    it('detects invalid parent component constraint', () => {
      const components = [
        {id: 'root', type: 'Surface', children: ['btn1']},
        {id: 'btn1', type: 'Button', parentId: 'root'}, // Button allowed only under Card
      ];
      const errors = validateComposition(components, 'root', catalog);
      assert.equal(errors.length, 1);
      assert.equal(errors[0].rule, 'allowed_parents');
    });

    it('detects invalid child component constraint', () => {
      const components = [
        {id: 'root', type: 'Surface', children: ['card1']},
        {id: 'card1', type: 'Card', parentId: 'root', children: ['badChild']},
        {id: 'badChild', type: 'Image', parentId: 'card1'}, // Card allows Text, Button only
      ];
      const errors = validateComposition(components, 'root', catalog);
      assert.equal(errors.length, 1);
      assert.equal(errors[0].rule, 'allowed_children');
    });
  });
});
