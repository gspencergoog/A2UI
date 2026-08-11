"""Unit tests for Python UAX #31 identifier validation."""

import pytest
from a2ui.core.validating.uax31 import is_valid_uax31_identifier


def test_valid_ascii_identifiers():
    assert is_valid_uax31_identifier("foo") is True
    assert is_valid_uax31_identifier("fooBar") is True
    assert is_valid_uax31_identifier("_privateVar") is True
    assert is_valid_uax31_identifier("var123") is True
    assert is_valid_uax31_identifier("_123") is True


def test_valid_unicode_identifiers():
    assert is_valid_uax31_identifier("café") is True
    assert is_valid_uax31_identifier("ñ_var") is True
    assert is_valid_uax31_identifier("α_beta") is True
    assert is_valid_uax31_identifier("日本語") is True


def test_invalid_identifiers():
    assert is_valid_uax31_identifier("") is False
    assert is_valid_uax31_identifier("123foo") is False
    assert is_valid_uax31_identifier("my-var") is False
    assert is_valid_uax31_identifier("foo bar") is False
    assert is_valid_uax31_identifier("hello.world") is False
    assert is_valid_uax31_identifier("foo@bar") is False
