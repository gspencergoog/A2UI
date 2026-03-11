/*
 * Copyright 2025 Google LLC
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

import { Types } from '../types';

/**
 * Represents a text chunk in the stream.
 */
export interface A2TextPayload {
  kind: 'text';
  /** The text content. */
  text: string;
}

/**
 * Represents a structural data chunk in the stream.
 */
export interface A2DataPayload {
  kind: 'data';
  /** The A2UI protocol message. */
  data: Types.ServerToClientMessage;
}

/**
 * Union type for payloads received from the server stream.
 * Can be a list of text/data chunks or an error object.
 */
export type A2AServerPayload = Array<A2DataPayload | A2TextPayload> | { error: string };
