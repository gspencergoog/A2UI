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
