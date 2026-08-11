/*
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

export const A2UI_MIME_TYPE = 'application/a2ui+json';
export const A2UI_MIME_TYPE_LEGACY = 'application/json+a2ui';

export function isA2uiMimeType(mimeType: string): boolean {
  if (!mimeType) return false;
  const normalized = mimeType.split(';')[0].trim().toLowerCase();
  return normalized === A2UI_MIME_TYPE || normalized === A2UI_MIME_TYPE_LEGACY;
}

export type SupportedProtocolVersion = 'v0.9' | 'v0.9.1' | 'v1.0';

export const SUPPORTED_PROTOCOL_VERSIONS: SupportedProtocolVersion[] = ['v0.9', 'v0.9.1', 'v1.0'];

export function isSupportedProtocolVersion(version: string): version is SupportedProtocolVersion {
  return (SUPPORTED_PROTOCOL_VERSIONS as string[]).includes(version);
}
