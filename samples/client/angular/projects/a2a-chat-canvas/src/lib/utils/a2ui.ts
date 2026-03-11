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

import { Part } from '@a2a-js/sdk';
import * as Types from '@a2ui/web_core/v0_9';
import { isA2aDataPart } from './type-guards';

/**
 * Extracts A2UI ServerToClientMessages from an array of A2A Parts.
 * It filters for parts that are A2A DataParts and checks for the presence of A2UI message keys
 * (createSurface, updateComponents, updateDataModel, deleteSurface).
 *
 * @param parts An array of A2A Parts.
 * @returns An array of A2UI Types.A2uiMessage objects.
 */
export function extractA2uiDataParts(parts: Part[]): Types.A2uiMessage[] {
  return parts.reduce<Types.A2uiMessage[]>((messages, part) => {
    if (isA2aDataPart(part)) {
      if (part.data && typeof part.data === 'object') {
        if ('createSurface' in part.data) {
          messages.push({
            version: 'v0.9',
            createSurface: part.data['createSurface'] as Types.CreateSurfaceMessage['createSurface'],
          });
        } else if ('updateComponents' in part.data) {
          messages.push({
            version: 'v0.9',
            updateComponents: part.data['updateComponents'] as Types.UpdateComponentsMessage['updateComponents'],
          });
        } else if ('updateDataModel' in part.data) {
          messages.push({
            version: 'v0.9',
            updateDataModel: part.data['updateDataModel'] as Types.UpdateDataModelMessage['updateDataModel'],
          });
        } else if ('deleteSurface' in part.data) {
          messages.push({
            version: 'v0.9',
            deleteSurface: part.data['deleteSurface'] as Types.DeleteSurfaceMessage['deleteSurface'],
          });
        }
      }
    }
    return messages;
  }, []);
}
