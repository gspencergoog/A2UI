# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        ExpressionEvaluationError: If invoked outside a collection scope, offset is non-integer, or result is negative.
    """
    if not isinstance(offset, int) or isinstance(offset, bool):
        raise ExpressionEvaluationError("@index() offset must be an integer.")

    if (
        scope is None
        or scope.index is None
        or isinstance(scope.index, bool)
        or scope.index < 0
    ):
        raise ExpressionEvaluationError(
            "@index() function can only be invoked within a Collection Scope (template"
            " loop context)."
        )
    result = scope.index + offset
    if result < 0:
        raise ExpressionEvaluationError("@index() resulting index cannot be negative.")
    return result
