/**
 * @fileoverview Built-in @index(offset?: int) evaluator for A2UI v1.0.
 *
 * Returns the current iteration index (plus optional integer offset) when invoked
 * within a Collection Scope context. Raises an error when called out of scope.
 */

export interface CollectionScopeContext {
  /** 0-based index of the current collection item */
  index: number;
}

export class ExpressionEvaluationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ExpressionEvaluationError';
  }
}

/**
 * Evaluates the @index function call.
 *
 * @param scope Optional collection scope context containing the current item index.
 * @param offset Optional integer offset to add to the 0-based index (defaults to 0).
 * @returns The calculated integer index.
 * @throws {ExpressionEvaluationError} If called outside a valid collection scope or if offset is not an integer.
 */
export function evaluateIndexFunction(scope?: CollectionScopeContext, offset: number = 0): number {
  if (!Number.isInteger(offset)) {
    throw new ExpressionEvaluationError('@index() offset must be an integer.');
  }
  if (!scope || scope.index === undefined || scope.index === null || scope.index < 0) {
    throw new ExpressionEvaluationError(
      '@index() function can only be invoked within a Collection Scope (template loop context).',
    );
  }
  return scope.index + offset;
}
