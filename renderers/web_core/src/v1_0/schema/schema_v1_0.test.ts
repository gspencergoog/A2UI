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

import {describe, it} from 'node:test';
import assert from 'node:assert/strict';
import {
  AgentToRendererMessageSchema,
  RendererToAgentMessageSchema,
  AgentCapabilitiesSchema,
  RendererCapabilitiesSchema,
  isA2uiMimeType,
  A2UI_MIME_TYPE,
  A2UI_MIME_TYPE_LEGACY,
} from './index.js';

describe('A2UI v1.0 Schema Validation Tests', () => {
  describe('MIME Type Constants & Fallback', () => {
    it('validates canonical and legacy MIME types', () => {
      assert.equal(isA2uiMimeType('application/a2ui+json'), true);
      assert.equal(isA2uiMimeType('application/json+a2ui'), true);
      assert.equal(isA2uiMimeType('APPLICATION/A2UI+JSON; charset=utf-8'), true);
      assert.equal(isA2uiMimeType('application/json'), false);
      assert.equal(isA2uiMimeType(''), false);
      assert.equal(A2UI_MIME_TYPE, 'application/a2ui+json');
      assert.equal(A2UI_MIME_TYPE_LEGACY, 'application/json+a2ui');
    });
  });

  describe('Agent-to-Renderer Schema (agent_to_renderer)', () => {
    it('validates v1.0 createSurface message', () => {
      const payload = {
        version: 'v1.0',
        createSurface: {
          surfaceId: 'surf_1',
          catalogId: 'cat_1',
          sendDataModel: true,
        },
      };
      const result = AgentToRendererMessageSchema.safeParse(payload);
      assert.equal(result.success, true);
    });

    it('validates v1.0 callRendererFunction message', () => {
      const payload = {
        version: 'v1.0',
        callRendererFunction: {
          functionCallId: 'call_123',
          callFunction: {
            call: 'getGeoLocation',
            catalogId: 'basic',
            args: {highAccuracy: true},
          },
        },
      };
      const result = AgentToRendererMessageSchema.safeParse(payload);
      assert.equal(result.success, true);
    });

    it('rejects callRendererFunction missing catalogId', () => {
      const payload = {
        version: 'v1.0',
        callRendererFunction: {
          functionCallId: 'call_123',
          callFunction: {
            call: 'getGeoLocation',
          },
        },
      };
      const result = AgentToRendererMessageSchema.safeParse(payload);
      assert.equal(result.success, false);
    });

    it('validates v1.0 agentFunctionResponse message', () => {
      const payload = {
        version: 'v1.0',
        agentFunctionResponse: {
          functionCallId: 'call_456',
          value: {latitude: 37.7749, longitude: -122.4194},
        },
      };
      const result = AgentToRendererMessageSchema.safeParse(payload);
      assert.equal(result.success, true);
    });

    it('validates v1.0 agentFunctionResponse error response', () => {
      const payload = {
        version: 'v1.0',
        agentFunctionResponse: {
          functionCallId: 'call_456',
          error: {
            code: 'PERMISSION_DENIED',
            message: 'User denied location access',
          },
        },
      };
      const result = AgentToRendererMessageSchema.safeParse(payload);
      assert.equal(result.success, true);
    });

    it('rejects agentFunctionResponse with both value and error', () => {
      const payload = {
        version: 'v1.0',
        agentFunctionResponse: {
          functionCallId: 'call_456',
          value: 'ok',
          error: {code: 'FAIL', message: 'err'},
        },
      };
      const result = AgentToRendererMessageSchema.safeParse(payload);
      assert.equal(result.success, false);
    });

    it('rejects unknown protocol version strings with UNSUPPORTED_PROTOCOL_VERSION', () => {
      const payload = {
        version: 'v0.8',
        createSurface: {
          surfaceId: 'surf_1',
        },
      };
      const result = AgentToRendererMessageSchema.safeParse(payload);
      assert.equal(result.success, false);
      if (!result.success) {
        const errText = JSON.stringify(result.error.issues);
        assert.match(errText, /UNSUPPORTED_PROTOCOL_VERSION/);
      }
    });

    it('accepts v0.9 and v0.9.1 versions', () => {
      const p09 = {
        version: 'v0.9',
        deleteSurface: {surfaceId: 's1'},
      };
      const p091 = {
        version: 'v0.9.1',
        deleteSurface: {surfaceId: 's1'},
      };
      assert.equal(AgentToRendererMessageSchema.safeParse(p09).success, true);
      assert.equal(AgentToRendererMessageSchema.safeParse(p091).success, true);
    });
  });

  describe('Renderer-to-Agent Schema (renderer_to_agent)', () => {
    it('validates v1.0 action message', () => {
      const payload = {
        version: 'v1.0',
        action: {
          name: 'buttonClick',
          surfaceId: 'surf_1',
          sourceComponentId: 'btn_1',
          timestamp: '2026-08-11T10:00:00.000Z',
          context: {count: 5},
        },
      };
      const result = RendererToAgentMessageSchema.safeParse(payload);
      assert.equal(result.success, true);
    });

    it('validates v1.0 callAgentFunction message', () => {
      const payload = {
        version: 'v1.0',
        callAgentFunction: {
          surfaceId: 'surf_1',
          functionCallId: 'func_999',
          callFunction: {
            call: 'calculateTax',
            args: {amount: 100},
          },
        },
      };
      const result = RendererToAgentMessageSchema.safeParse(payload);
      assert.equal(result.success, true);
    });

    it('validates v1.0 rendererFunctionResponse message', () => {
      const payload = {
        version: 'v1.0',
        rendererFunctionResponse: {
          functionCallId: 'call_123',
          value: 'success',
        },
      };
      const result = RendererToAgentMessageSchema.safeParse(payload);
      assert.equal(result.success, true);
    });

    it('validates surface-level error payload', () => {
      const payload = {
        version: 'v1.0',
        error: {
          code: 'RENDER_FAILED',
          message: 'Surface render crashed',
          surfaceId: 'surf_1',
        },
      };
      const result = RendererToAgentMessageSchema.safeParse(payload);
      assert.equal(result.success, true);
    });

    it('validates functionCall-level error payload', () => {
      const payload = {
        version: 'v1.0',
        error: {
          code: 'EXECUTION_TIMEOUT',
          message: 'Function execution timed out',
          functionCallId: 'func_999',
        },
      };
      const result = RendererToAgentMessageSchema.safeParse(payload);
      assert.equal(result.success, true);
    });

    it('ENFORCES MUTUAL EXCLUSIVITY: rejects error specifying BOTH surfaceId and functionCallId', () => {
      const payload = {
        version: 'v1.0',
        error: {
          code: 'AMBIGUOUS_ERROR',
          message: 'Conflict',
          surfaceId: 'surf_1',
          functionCallId: 'func_999',
        },
      };
      const result = RendererToAgentMessageSchema.safeParse(payload);
      assert.equal(
        result.success,
        false,
        'Error with both surfaceId and functionCallId MUST fail validation',
      );
    });

    it('rejects validation errors lacking path or surfaceId', () => {
      const payload = {
        version: 'v1.0',
        error: {
          code: 'VALIDATION_FAILED',
          message: 'Missing path',
        },
      };
      const result = RendererToAgentMessageSchema.safeParse(payload);
      assert.equal(result.success, false);
    });
  });

  describe('Capabilities Schemas', () => {
    it('validates AgentCapabilities', () => {
      const caps = {
        'v1.0': {
          supportedCatalogIds: ['basic'],
          acceptsInlineCatalogs: true,
        },
      };
      assert.equal(AgentCapabilitiesSchema.safeParse(caps).success, true);
    });

    it('validates RendererCapabilities', () => {
      const caps = {
        'v1.0': {
          supportedCatalogIds: ['basic'],
          inlineCatalogs: [{catalogId: 'custom'}],
        },
      };
      assert.equal(RendererCapabilitiesSchema.safeParse(caps).success, true);
    });
  });
});
