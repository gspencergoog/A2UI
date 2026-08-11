/**
 * @fileoverview Zod schemas and types for A2UI v1.0 Catalog Definitions.
 */

import {z} from 'zod';
import {isValidUax31Identifier} from '../validating/uax31.js';

/**
 * Component definition schema including composition rules (allowedParents, allowedChildren).
 */
export const ComponentDefinitionSchema = z.object({
  allowedParents: z.array(z.string()).optional(),
  allowedChildren: z.array(z.string()).optional(),
  metadata: z.record(z.unknown()).optional(),
});

export type ComponentDefinition = z.infer<typeof ComponentDefinitionSchema>;

/**
 * Function definition schema including returnType, callableFrom, and activation requirements.
 */
export const FunctionDefinitionSchema = z.object({
  returnType: z.enum(['string', 'number', 'boolean', 'array', 'object', 'any', 'void']),
  callableFrom: z
    .enum(['rendererOnly', 'agentOnly', 'rendererOrAgent'])
    .optional()
    .default('rendererOnly'),
  requiresUserActivation: z.boolean().optional().default(false),
  description: z.string().optional(),
  properties: z.record(z.unknown()).optional(),
});

export type FunctionDefinition = z.infer<typeof FunctionDefinitionSchema>;

/**
 * Catalog definition schema for A2UI v1.0.
 * Map-based functions and components where keys must satisfy UAX #31.
 */
export const CatalogDefinitionSchema = z.object({
  protocolVersion: z.string().optional().default('1.0'),
  catalogId: z.string(),
  title: z.string().optional(),
  description: z.string().optional(),
  instructions: z.string().optional(),
  components: z
    .record(
      z
        .string()
        .refine(isValidUax31Identifier, {
          message: 'Component name must be a valid UAX #31 identifier',
        })
        .refine(name => name !== 'Surface', {
          message: 'Component name cannot be Surface',
        }),
      ComponentDefinitionSchema,
    )
    .optional(),
  functions: z
    .record(
      z.string().refine(isValidUax31Identifier, {
        message: 'Function name must be a valid UAX #31 identifier',
      }),
      FunctionDefinitionSchema,
    )
    .optional(),
});

export type CatalogDefinition = Omit<z.infer<typeof CatalogDefinitionSchema>, 'protocolVersion'> & {
  protocolVersion?: string;
};
