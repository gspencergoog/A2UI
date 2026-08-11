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
import {AnyComponentSchema} from '../../v0_9/schema/common-types.js';
import {SupportedProtocolVersion, SUPPORTED_PROTOCOL_VERSIONS} from './constants.js';

export const VersionSchema = z.string().refine(
  val => (SUPPORTED_PROTOCOL_VERSIONS as string[]).includes(val),
  val => ({message: `UNSUPPORTED_PROTOCOL_VERSION: ${val}`}),
);

export const ComponentItemSchema = z
  .object({
    id: z.string(),
    component: z.string().optional(),
  })
  .passthrough();

export const CreateSurfaceMessageSchema = z
  .object({
    version: VersionSchema,
    createSurface: z
      .object({
        surfaceId: z.string().describe('The unique identifier for the UI surface to be rendered.'),
        catalogId: z.string().optional().describe('Default catalog identifier.'),
        theme: z.any().optional().describe('Theme parameters for the surface.'),
        sendDataModel: z.boolean().optional().describe('If true, client sends full data model.'),
        components: z.array(ComponentItemSchema).optional().describe('Initial component tree.'),
        dataModel: z.record(z.any()).optional().describe('Initial data model.'),
        metadata: z.record(z.any()).optional().describe('Optional surface-level metadata.'),
      })
      .strict(),
  })
  .strict();

export const UpdateComponentsMessageSchema = z
  .object({
    version: VersionSchema,
    updateComponents: z
      .object({
        surfaceId: z.string().describe('The unique identifier for the UI surface to be updated.'),
        components: z
          .array(ComponentItemSchema)
          .min(1)
          .describe('A list containing UI components for the surface.'),
      })
      .strict(),
  })
  .strict();

export const UpdateDataModelMessageSchema = z
  .object({
    version: VersionSchema,
    updateDataModel: z
      .object({
        surfaceId: z
          .string()
          .describe('The unique identifier for the UI surface this data model update applies to.'),
        path: z.string().optional().describe('An optional path within the data model.'),
        value: z.any().describe('The data to be updated in the data model.'),
      })
      .strict(),
  })
  .strict();

export const DeleteSurfaceMessageSchema = z
  .object({
    version: VersionSchema,
    deleteSurface: z
      .object({
        surfaceId: z.string().describe('The unique identifier for the UI surface to be deleted.'),
      })
      .strict(),
  })
  .strict();

export const CallRendererFunctionMessageSchema = z
  .object({
    version: VersionSchema,
    callRendererFunction: z
      .object({
        functionCallId: z.string().describe('Unique function call identifier.'),
        callFunction: z
          .object({
            call: z.string().describe('Name of the function to invoke.'),
            catalogId: z.string().describe('Catalog ID for the function.'),
            args: z.record(z.any()).optional().describe('Arguments for the function.'),
          })
          .strict(),
      })
      .strict(),
  })
  .strict();

export const FunctionResponsePayloadSchema = z
  .object({
    functionCallId: z.string().describe('Unique function call identifier.'),
    value: z.any().optional(),
    error: z
      .object({
        code: z.string(),
        message: z.string(),
      })
      .strict()
      .optional(),
  })
  .strict()
  .refine(
    data =>
      (data.value !== undefined && data.error === undefined) ||
      (data.value === undefined && data.error !== undefined),
    {message: 'FunctionResponse must contain either value or error, but not both or neither.'},
  );

export const AgentFunctionResponseMessageSchema = z
  .object({
    version: VersionSchema,
    agentFunctionResponse: FunctionResponsePayloadSchema,
  })
  .strict();

export const AgentToRendererMessageSchema = z.union([
  CreateSurfaceMessageSchema,
  UpdateComponentsMessageSchema,
  UpdateDataModelMessageSchema,
  DeleteSurfaceMessageSchema,
  CallRendererFunctionMessageSchema,
  AgentFunctionResponseMessageSchema,
]);

export type CreateSurfaceMessage = z.infer<typeof CreateSurfaceMessageSchema>;
export type UpdateComponentsMessage = z.infer<typeof UpdateComponentsMessageSchema>;
export type UpdateDataModelMessage = z.infer<typeof UpdateDataModelMessageSchema>;
export type DeleteSurfaceMessage = z.infer<typeof DeleteSurfaceMessageSchema>;
export type CallRendererFunctionMessage = z.infer<typeof CallRendererFunctionMessageSchema>;
export type AgentFunctionResponseMessage = z.infer<typeof AgentFunctionResponseMessageSchema>;

export type AgentToRendererMessage = z.infer<typeof AgentToRendererMessageSchema>;

export const AgentToRendererMessageListSchema = z.array(AgentToRendererMessageSchema);
export type AgentToRendererMessageList = z.infer<typeof AgentToRendererMessageListSchema>;

export const AgentToRendererMessageListWrapperSchema = z
  .object({
    messages: AgentToRendererMessageListSchema,
  })
  .strict();
export type AgentToRendererMessageListWrapper = z.infer<
  typeof AgentToRendererMessageListWrapperSchema
>;

// Backward-compatibility aliases
export const ServerToClientMessageSchema = AgentToRendererMessageSchema;
export type ServerToClientMessage = AgentToRendererMessage;
export const A2uiMessageSchema = AgentToRendererMessageSchema;
export type A2uiMessage = AgentToRendererMessage;
export const A2uiMessageListSchema = AgentToRendererMessageListSchema;
export type A2uiMessageList = AgentToRendererMessageList;
export const A2uiMessageListWrapperSchema = AgentToRendererMessageListWrapperSchema;
export type A2uiMessageListWrapper = AgentToRendererMessageListWrapper;
