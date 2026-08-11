import {describe, it} from 'node:test';
import assert from 'node:assert/strict';
import {isValidUax31Identifier} from './uax31.js';

describe('isValidUax31Identifier', () => {
  it('should return true for valid ASCII identifiers', () => {
    assert.equal(isValidUax31Identifier('foo'), true);
    assert.equal(isValidUax31Identifier('fooBar'), true);
    assert.equal(isValidUax31Identifier('_privateVar'), true);
    assert.equal(isValidUax31Identifier('var123'), true);
    assert.equal(isValidUax31Identifier('_123'), true);
  });

  it('should return true for valid Unicode identifiers', () => {
    assert.equal(isValidUax31Identifier('café'), true);
    assert.equal(isValidUax31Identifier('ñ_var'), true);
    assert.equal(isValidUax31Identifier('α_beta'), true);
    assert.equal(isValidUax31Identifier('日本語'), true);
  });

  it('should return false for invalid identifiers', () => {
    assert.equal(isValidUax31Identifier(''), false);
    assert.equal(isValidUax31Identifier('123foo'), false);
    assert.equal(isValidUax31Identifier('my-var'), false);
    assert.equal(isValidUax31Identifier('foo bar'), false);
    assert.equal(isValidUax31Identifier('hello.world'), false);
    assert.equal(isValidUax31Identifier('foo@bar'), false);
  });
});
