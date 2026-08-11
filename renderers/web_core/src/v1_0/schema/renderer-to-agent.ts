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
import {VersionSchema, FunctionResponsePayloadSchema} from './agent-to-renderer.js';

export const ActionPayloadSchema = z
  .object({
    name: z.string().describe('The name of the action from action.event.name.'),
    surfaceId: z.string().describe('Surface ID where event originated.'),
    sourceComponentId: z.string().describe('Component ID that triggered event.'),
    timestamp: z.string().datetime().describe('ISO 8601 timestamp.'),
    context: z.record(z.unknown()).describe('Action context key-value pairs.'),
    metadata: z.record(z.unknown()).optional().describe('Optional action metadata.'),
  })
  .strict();

export const ValidationErrorPayloadSchema = z
  .object({
    code: z.enum(['VALIDATION_FAILED', 'UNALLOWED_PARENT', 'UNALLOWED_CHILD']),
    surfaceId: z.string().describe('Surface ID where error occurred.'),
    path: z.string().describe('JSON pointer path that failed validation.'),
    message: z.string().describe('Validation error message.'),
  })
  .strict();

export const GenericErrorWithSurfaceIdSchema = z
  .object({
    code: z
      .string()
      .refine(c => !['VALIDATION_FAILED', 'UNALLOWED_PARENT', 'UNALLOWED_CHILD'].includes(c)),
    message: z.string(),
    surfaceId: z.string(),
  })
  .strict();

export const GenericErrorWithFunctionCallIdSchema = z
  .object({
    code: z
      .string()
      .refine(c => !['VALIDATION_FAILED', 'UNALLOWED_PARENT', 'UNALLOWED_CHILD'].includes(c)),
    message: z.string(),
    functionCallId: z.string(),
  })
  .strict();

export const RendererToAgentErrorPayloadSchema = z.union([
  ValidationErrorPayloadSchema,
  GenericErrorWithSurfaceIdSchema,
  GenericErrorWithFunctionCallIdSchema,
]);

export const ActionMessageSchema = z
  .object({
    version: VersionSchema,
    action: ActionPayloadSchema,
  })
  .strict();

export const CallAgentFunctionMessageSchema = z
  .object({
    version: VersionSchema,
    callAgentFunction: z
      .object({
        surfaceId: z.string(),
        functionCallId: z.string(),
        callFunction: z
          .object({
            call: z.string(),
            catalogId: z.string().optional(),
            args: z.record(z.unknown()).optional(),
          })
          .strict(),
      })
      .strict(),
  })
  .strict();

export const RendererFunctionResponseMessageSchema = z
  .object({
    version: VersionSchema,
    rendererFunctionResponse: FunctionResponsePayloadSchema,
  })
  .strict();

export const ErrorMessageSchema = z
  .object({
    version: VersionSchema,
    error: RendererToAgentErrorPayloadSchema,
  })
  .strict();

export const RendererToAgentMessageSchema = z.union([
  ActionMessageSchema,
  CallAgentFunctionMessageSchema,
  RendererFunctionResponseMessageSchema,
  ErrorMessageSchema,
]);

export type ActionMessage = z.infer<typeof ActionMessageSchema>;
export type CallAgentFunctionMessage = z.infer<typeof CallAgentFunctionMessageSchema>;
export type RendererFunctionResponseMessage = z.infer<typeof RendererFunctionResponseMessageSchema>;
export type ErrorMessage = z.infer<typeof ErrorMessageSchema>;

export type RendererToAgentMessage = z.infer<typeof RendererToAgentMessageSchema>;

export const RendererToAgentMessageListSchema = z.array(RendererToAgentMessageSchema);
export type RendererToAgentMessageList = z.infer<typeof RendererToAgentMessageListSchema>;

export const RendererToAgentMessageListWrapperSchema = z
  .object({
    messages: RendererToAgentMessageListSchema,
  })
  .strict();
export type RendererToAgentMessageListWrapper = z.infer<
  typeof RendererToAgentMessageListWrapperSchema
>;

export const A2uiClientDataModelSchema = z
  .object({
    version: VersionSchema,
    surfaces: z
      .record(z.object({}).passthrough())
      .describe('A map of surface IDs to their current data models.'),
  })
  .strict();
export type A2uiClientDataModel = z.infer<typeof A2uiClientDataModelSchema>;

// Backward-compatibility aliases
export const ClientToServerMessageSchema = RendererToAgentMessageSchema;
export type ClientToServerMessage = RendererToAgentMessage;
export const A2uiClientMessageSchema = RendererToAgentMessageSchema;
export type A2uiClientMessage = RendererToAgentMessage;
export const A2uiClientActionMessageSchema = ActionMessageSchema;
export type A2uiClientActionMessage = ActionMessage;
export const A2uiClientErrorMessageSchema = ErrorMessageSchema;
export type A2uiClientErrorMessage = ErrorMessage;
export const A2uiClientActionSchema = ActionPayloadSchema;
export type A2uiClientAction = z.infer<typeof ActionPayloadSchema>;
