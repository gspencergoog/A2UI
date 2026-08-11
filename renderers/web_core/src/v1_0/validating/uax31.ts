/**
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

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
