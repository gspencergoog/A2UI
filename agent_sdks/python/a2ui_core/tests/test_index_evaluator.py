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

"""Unit tests for Python @index evaluator."""

import pytest
from a2ui.core.expressions.index_evaluator import (
    CollectionScopeContext,
    ExpressionEvaluationError,
    evaluate_index_function,
)


def test_index_function_basic():
    assert evaluate_index_function(CollectionScopeContext(index=0)) == 0
    assert evaluate_index_function(CollectionScopeContext(index=5)) == 5


def test_index_function_offsets():
    assert evaluate_index_function(CollectionScopeContext(index=0), offset=1) == 1
    assert evaluate_index_function(CollectionScopeContext(index=2), offset=1) == 3
    assert evaluate_index_function(CollectionScopeContext(index=5), offset=-1) == 4


def test_index_function_non_integer_offset():
    with pytest.raises(ExpressionEvaluationError, match="must be an integer"):
        evaluate_index_function(CollectionScopeContext(index=0), offset=1.5)


def test_index_function_negative_result():
    with pytest.raises(ExpressionEvaluationError, match="cannot be negative"):
        evaluate_index_function(CollectionScopeContext(index=0), offset=-5)


def test_index_function_out_of_scope():
    with pytest.raises(ExpressionEvaluationError, match="Collection Scope"):
        evaluate_index_function(None)


def test_index_function_negative_index():
    with pytest.raises(ExpressionEvaluationError):
        evaluate_index_function(CollectionScopeContext(index=-1))
