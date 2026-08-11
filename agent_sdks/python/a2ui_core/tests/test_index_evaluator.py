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


def test_index_function_out_of_scope():
    with pytest.raises(ExpressionEvaluationError, match="Collection Scope"):
        evaluate_index_function(None)


def test_index_function_negative_index():
    with pytest.raises(ExpressionEvaluationError):
        evaluate_index_function(CollectionScopeContext(index=-1))
