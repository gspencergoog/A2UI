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
