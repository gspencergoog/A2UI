/**
 * @fileoverview Unicode UAX #31 Identifier Validator for A2UI v1.0.
 *
 * Enforces UAX #31 identifier constraints across component names, property keys,
 * function names, event names, and extension metadata keys.
 */

/**
 * Regex enforcing UAX #31 identifier syntax with unicode property escapes:
 * Starts with ID_Start or underscore, followed by zero or more ID_Continue characters.
 */
export const UAX31_IDENTIFIER_REGEX = /^[\p{ID_Start}_][\p{ID_Continue}]*$/u;

/**
 * Validates whether a given string is a valid UAX #31 identifier.
 *
 * @param identifier - The string identifier to validate.
 * @returns True if valid UAX #31 identifier, false otherwise.
 */
export function isValidUax31Identifier(identifier: string): boolean {
  if (!identifier || typeof identifier !== 'string') {
    return false;
  }
  return UAX31_IDENTIFIER_REGEX.test(identifier);
}
