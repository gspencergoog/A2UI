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
