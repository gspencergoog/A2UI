"""Built-in @index(offset?: int) function evaluator for A2UI v1.0 in Python."""

from typing import Optional
from pydantic import BaseModel


class CollectionScopeContext(BaseModel):
    """Collection scope context model."""

    index: int


class ExpressionEvaluationError(Exception):
    """Raised when expression evaluation fails or is out of scope."""

    pass


def evaluate_index_function(
    scope: Optional[CollectionScopeContext] = None, offset: int = 0
) -> int:
    """Evaluates the @index function.

    Args:
        scope: Collection scope context containing current item index.
        offset: Integer offset to add to the 0-based index.

    Returns:
        The calculated index integer.

    Raises:
        ExpressionEvaluationError: If invoked outside a collection scope or offset is non-integer.
    """
    if not isinstance(offset, int) or isinstance(offset, bool):
        raise ExpressionEvaluationError("@index() offset must be an integer.")

    if scope is None or scope.index is None or scope.index < 0:
        raise ExpressionEvaluationError(
            "@index() function can only be invoked within a Collection Scope (template loop context)."
        )
    return scope.index + offset
