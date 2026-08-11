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

export type JsonSchema = Record<string, any>;

export interface FunctionDefinition {
  name: string;
  description?: string;
  parameters: JsonSchema;
  returnType: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'any' | 'void';
}

export interface InlineCatalog {
  catalogId: string;
  components?: Record<string, JsonSchema>;
  functions?: FunctionDefinition[];
  theme?: Record<string, JsonSchema>;
}

export const AgentCapabilitiesV1_0Schema = z
  .object({
    supportedCatalogIds: z.array(z.string()).optional(),
    acceptsInlineCatalogs: z.boolean().optional().default(false),
  })
  .strict();

export const AgentCapabilitiesV0_9Schema = z
  .object({
    supportedCatalogIds: z.array(z.string()).optional(),
    acceptsInlineCatalogs: z.boolean().optional().default(false),
  })
  .strict();

export const AgentCapabilitiesSchema = z
  .object({
    'v1.0': AgentCapabilitiesV1_0Schema.optional(),
    'v0.9': AgentCapabilitiesV0_9Schema.optional(),
    'v0.9.1': AgentCapabilitiesV0_9Schema.optional(),
  })
  .strict();

export type AgentCapabilitiesV1_0 = z.infer<typeof AgentCapabilitiesV1_0Schema>;
export type AgentCapabilitiesV0_9 = z.infer<typeof AgentCapabilitiesV0_9Schema>;
export type AgentCapabilities = z.infer<typeof AgentCapabilitiesSchema>;
