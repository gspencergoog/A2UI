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

import {describe, it} from 'node:test';
import * as assert from 'node:assert';
import {readFileSync, existsSync} from 'node:fs';
import {resolve, join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {AgentToRendererMessageSchema, RendererToAgentMessageSchema} from './index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function findSpecDir(): string {
  let current = __dirname;
  for (let i = 0; i < 10; i++) {
    const candidate = resolve(current, 'specification/v1_0/json');
    if (existsSync(candidate)) return candidate;
    const parent = dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return resolve(__dirname, '../../../../../../specification/v1_0/json');
}

const SPEC_DIR_V1_0 = findSpecDir();

describe('A2UI Schema Verification v1.0', () => {
  it('verifies v1.0 json spec files exist and parse', () => {
    const a2rPath = join(SPEC_DIR_V1_0, 'agent_to_renderer.json');
    const r2aPath = join(SPEC_DIR_V1_0, 'renderer_to_agent.json');
    assert.equal(existsSync(a2rPath), true, `Spec file not found at ${a2rPath}`);
    assert.equal(existsSync(r2aPath), true, `Spec file not found at ${r2aPath}`);

    const a2r = JSON.parse(readFileSync(a2rPath, 'utf-8'));
    const r2a = JSON.parse(readFileSync(r2aPath, 'utf-8'));

    assert.equal(a2r.title, 'A2UI Message Schema');
    assert.equal(r2a.title, 'A2UI (Agent to UI) Renderer-to-Agent Event Schema');
  });

  it('validates AgentToRenderer v1.0 schema against all message types in spec', () => {
    const createSurface = {
      version: 'v1.0',
      createSurface: {
        surfaceId: 'surface-1',
        catalogId: 'cat-1',
        sendDataModel: true,
        components: [{id: 'root', component: 'Box'}],
      },
    };
    const updateComponents = {
      version: 'v1.0',
      updateComponents: {
        surfaceId: 'surface-1',
        components: [{id: 'root', component: 'Box'}],
      },
    };
    const updateDataModel = {
      version: 'v1.0',
      updateDataModel: {
        surfaceId: 'surface-1',
        path: '/user',
        value: {name: 'Alice'},
      },
    };
    const deleteSurface = {
      version: 'v1.0',
      deleteSurface: {surfaceId: 'surface-1'},
    };
    const callRendererFunction = {
      version: 'v1.0',
      callRendererFunction: {
        functionCallId: 'func-1',
        callFunction: {call: 'getLocation', catalogId: 'basic'},
      },
    };
    const agentFunctionResponse = {
      version: 'v1.0',
      agentFunctionResponse: {
        functionCallId: 'func-1',
        value: {status: 'ok'},
      },
    };

    assert.deepStrictEqual(AgentToRendererMessageSchema.parse(createSurface), createSurface);
    assert.deepStrictEqual(AgentToRendererMessageSchema.parse(updateComponents), updateComponents);
    assert.deepStrictEqual(AgentToRendererMessageSchema.parse(updateDataModel), updateDataModel);
    assert.deepStrictEqual(AgentToRendererMessageSchema.parse(deleteSurface), deleteSurface);
    assert.deepStrictEqual(
      AgentToRendererMessageSchema.parse(callRendererFunction),
      callRendererFunction,
    );
    assert.deepStrictEqual(
      AgentToRendererMessageSchema.parse(agentFunctionResponse),
      agentFunctionResponse,
    );
  });

  it('validates RendererToAgent v1.0 schema against all event types in spec', () => {
    const action = {
      version: 'v1.0',
      action: {
        name: 'submit',
        surfaceId: 'surface-1',
        sourceComponentId: 'btn-1',
        timestamp: '2026-08-11T10:00:00.000Z',
        context: {},
      },
    };
    const callAgentFunction = {
      version: 'v1.0',
      callAgentFunction: {
        surfaceId: 'surface-1',
        functionCallId: 'func-2',
        callFunction: {call: 'computeHash'},
      },
    };
    const rendererFunctionResponse = {
      version: 'v1.0',
      rendererFunctionResponse: {
        functionCallId: 'func-3',
        value: {hash: 'abc'},
      },
    };
    const errorSurface = {
      version: 'v1.0',
      error: {
        code: 'CRASH',
        message: 'crashed',
        surfaceId: 'surface-1',
      },
    };

    assert.deepStrictEqual(RendererToAgentMessageSchema.parse(action), action);
    assert.deepStrictEqual(
      RendererToAgentMessageSchema.parse(callAgentFunction),
      callAgentFunction,
    );
    assert.deepStrictEqual(
      RendererToAgentMessageSchema.parse(rendererFunctionResponse),
      rendererFunctionResponse,
    );
    assert.deepStrictEqual(RendererToAgentMessageSchema.parse(errorSurface), errorSurface);
  });
});
