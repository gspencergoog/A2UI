# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from inspect_ai.solver import Solver, solver, TaskState, Generate
from inspect_ai.model import ChatMessageSystem, ModelOutput, ChatCompletionChoice, ChatMessageAssistant
from a2ui.express.prompt_generator import ExpressPromptGenerator
from a2ui.express.compiler import ExpressCompiler
from ..shared.utils import measured_generate

@solver
def a2ui_express_prompt(catalog_path: str) -> Solver:
    """Solver to inject A2UI Express prompt contract instructions."""
    generator = ExpressPromptGenerator(catalog_path)
    prompt = generator.generate_prompt()

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.messages.insert(0, ChatMessageSystem(content=prompt))
        return state
        
    return solve

import re

@solver
def compile_express_dsl(catalog_path: str) -> Solver:
    """Solver to compile generated A2UI Express DSL back to standard JSON."""
    compiler = ExpressCompiler(catalog_path)

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        if not state.output or not state.output.completion:
            return state

        completion = state.output.completion.strip()

        # Try to extract target surface ID from the prompt input
        prompt_text = state.input if isinstance(state.input, str) else str(state.input)
        surface_id_match = re.search(
            r"surface(?:Id)?(?:\s+of)?\s+['\"]([^'\"]+)['\"]",
            prompt_text,
            re.IGNORECASE
        )
        surface_id = surface_id_match.group(1) if surface_id_match else "eval_surface"

        # 1. Check if the model output is standard JSON wrapped in <a2ui-json> tags
        if "<a2ui-json>" in completion:
            try:
                start_idx = completion.find("<a2ui-json>") + len("<a2ui-json>")
                end_idx = completion.find("</a2ui-json>")
                json_content = completion[start_idx:end_idx].strip()
                messages = json.loads(json_content)
                
                # Standardize to v0.9 messages
                if isinstance(messages, list):
                    for msg in messages:
                        if isinstance(msg, dict):
                            msg["version"] = "v0.9"
                            # Make sure surface ID matches if it contains operations
                            for key in ["createSurface", "updateComponents", "updateDataModel", "deleteSurface"]:
                                if key in msg and isinstance(msg[key], dict):
                                    msg[key]["surfaceId"] = surface_id

                            # Handle hybrid inline DSL compilation
                            if "updateComponents" in msg and isinstance(msg["updateComponents"], dict):
                                uc = msg["updateComponents"]
                                if "dsl" in uc and isinstance(uc["dsl"], str):
                                    inner_dsl = uc["dsl"].strip()
                                    if "<a2ui>" in inner_dsl:
                                        s_idx = inner_dsl.find("<a2ui>") + len("<a2ui>")
                                        e_idx = inner_dsl.find("</a2ui>")
                                        inner_dsl = inner_dsl[s_idx:e_idx].strip()
                                    compiled_inner = compiler.compile(inner_dsl, surface_id=surface_id)
                                    uc.pop("dsl")
                                    uc["components"] = compiled_inner["createSurface"].get("components", [])

                    formatted = f"<a2ui-json>\n{json.dumps(messages, indent=2)}\n</a2ui-json>"
                    state.output = ModelOutput(
                        model=state.output.model,
                        choices=[ChatCompletionChoice(message=ChatMessageAssistant(content=formatted))]
                    )
                    return state
            except Exception:
                # If JSON parsing failed, fall back to compiling the string as DSL
                pass

        # 2. Extract DSL content inside <a2ui> tags if present, or clean markdown blocks
        dsl_content = completion
        if "<a2ui>" in completion:
            start_idx = completion.find("<a2ui>") + len("<a2ui>")
            end_idx = completion.find("</a2ui>")
            dsl_content = completion[start_idx:end_idx].strip()
        else:
            if dsl_content.startswith("```"):
                lines = dsl_content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                dsl_content = "\n".join(lines).strip()

        try:
            compiled_json = compiler.compile(dsl_content, surface_id=surface_id)
            
            # v0.9 separating logic
            extracted_create = compiled_json.get("createSurface", {})
            catalog_id = extracted_create.get("catalogId", "")
            components = extracted_create.get("components", [])
            data_model = extracted_create.get("dataModel", {})
            
            messages = []
            
            # Message 1: createSurface (no inline components or dataModel under v0.9)
            messages.append({
                "version": "v0.9",
                "createSurface": {
                    "surfaceId": surface_id,
                    "catalogId": catalog_id
                }
            })
            
            # Message 2: updateComponents
            if components:
                messages.append({
                    "version": "v0.9",
                    "updateComponents": {
                        "surfaceId": surface_id,
                        "components": components
                    }
                })
                
            # Message 3: updateDataModel (if dataModel is not empty)
            if data_model:
                messages.append({
                    "version": "v0.9",
                    "updateDataModel": {
                        "surfaceId": surface_id,
                        "value": data_model
                    }
                })

            formatted = f"<a2ui-json>\n{json.dumps(messages, indent=2)}\n</a2ui-json>"
            state.output = ModelOutput(
                model=state.output.model,
                choices=[ChatCompletionChoice(message=ChatMessageAssistant(content=formatted))]
            )
        except Exception as e:
            state.output = ModelOutput(
                model=state.output.model,
                choices=[ChatCompletionChoice(message=ChatMessageAssistant(content=f"Compilation failed: {e}\nRaw output:\n{dsl_content}"))]
            )
        return state
        
    return solve

def express_solver(schema_path: str, catalog_path: str) -> list[Solver]:
    """Returns the solver chain for the 'express' evaluation strategy."""
    return [
        a2ui_express_prompt(catalog_path),
        measured_generate(),
        compile_express_dsl(catalog_path)
    ]
