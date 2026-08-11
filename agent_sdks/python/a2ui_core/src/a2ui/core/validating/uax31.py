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

"""Unicode UAX #31 Identifier Validator for A2UI v1.0.

Enforces UAX #31 identifier constraints across component names, property keys,
function names, event names, and extension metadata keys.
"""


def is_valid_uax31_identifier(identifier: str) -> bool:
    """Validates whether a given string is a valid UAX #31 identifier.

    Args:
        identifier: The string identifier to validate.

    Returns:
        True if valid UAX #31 identifier, False otherwise.
    """
    if not isinstance(identifier, str) or not identifier:
        return False
    return identifier.isidentifier()
