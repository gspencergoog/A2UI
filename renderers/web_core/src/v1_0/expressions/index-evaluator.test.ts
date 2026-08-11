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
import {evaluateIndexFunction, ExpressionEvaluationError} from './index-evaluator.js';

describe('@index Evaluator Tests (v1.0)', () => {
  it('returns 0-based index without offset', () => {
    assert.equal(evaluateIndexFunction({index: 0}), 0);
    assert.equal(evaluateIndexFunction({index: 5}), 5);
  });

  it('applies positive and negative integer offsets correctly', () => {
    assert.equal(evaluateIndexFunction({index: 0}, 1), 1);
    assert.equal(evaluateIndexFunction({index: 2}, 1), 3);
    assert.equal(evaluateIndexFunction({index: 5}, -1), 4);
  });

  it('throws ExpressionEvaluationError when offset is non-integer', () => {
    assert.throws(() => evaluateIndexFunction({index: 0}, 1.5), ExpressionEvaluationError);
  });

  it('throws ExpressionEvaluationError when resulting index is negative', () => {
    assert.throws(() => evaluateIndexFunction({index: 0}, -5), ExpressionEvaluationError);
  });

  it('throws ExpressionEvaluationError when invoked outside Collection Scope', () => {
    assert.throws(
      () => evaluateIndexFunction(undefined),
      (err: any) =>
        err instanceof ExpressionEvaluationError && err.message.includes('Collection Scope'),
    );
  });

  it('throws ExpressionEvaluationError when index is negative or invalid', () => {
    assert.throws(() => evaluateIndexFunction({index: -1}), ExpressionEvaluationError);
  });
});
