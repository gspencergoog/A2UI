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
