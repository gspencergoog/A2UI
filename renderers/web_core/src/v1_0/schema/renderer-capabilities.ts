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

import {z} from 'zod';
import {InlineCatalog} from './agent-capabilities.js';

export const RendererCapabilitiesV1_0Schema = z
  .object({
    supportedCatalogIds: z.array(z.string()),
    inlineCatalogs: z.array(z.record(z.any())).optional(),
  })
  .strict();

export const RendererCapabilitiesV0_9Schema = z
  .object({
    supportedCatalogIds: z.array(z.string()),
    inlineCatalogs: z.array(z.record(z.any())).optional(),
  })
  .strict();

export const RendererCapabilitiesSchema = z
  .object({
    'v1.0': RendererCapabilitiesV1_0Schema.optional(),
    'v0.9': RendererCapabilitiesV0_9Schema.optional(),
    'v0.9.1': RendererCapabilitiesV0_9Schema.optional(),
  })
  .strict();

export type RendererCapabilitiesV1_0 = z.infer<typeof RendererCapabilitiesV1_0Schema>;
export type RendererCapabilitiesV0_9 = z.infer<typeof RendererCapabilitiesV0_9Schema>;
export type RendererCapabilities = z.infer<typeof RendererCapabilitiesSchema>;

// Backward compatibility aliases for client capabilities
export type A2uiClientCapabilities = RendererCapabilities;
export type A2uiVersionCapabilities = RendererCapabilitiesV0_9;
export type {InlineCatalog};
