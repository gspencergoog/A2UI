# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Prompt compiler for A2UI Atom inference format."""

from typing import Any, Optional, TYPE_CHECKING
from a2ui.prompt import PromptGenerator
from a2ui.core.schema.client_capabilities import V09Capabilities
# CatalogSchemaHelper import handled lazily inside class

if TYPE_CHECKING:
    from .format import AtomFormat

ATOM_RULES = r'''# A2UI Atom Output Contract

You must output the user interface using the compact A2UI Atom S-Expression notation.
You MUST surround the entire A2UI Atom block with the sentinel tags `<a2ui>` and `</a2ui>`.

IMPORTANT: Wrap your output inside `<a2ui>` and `</a2ui>` sentinel tags. Do NOT output raw JSON messages.

## Grammar Rules

1. Every component node is a parenthesized expression starting with the ComponentName:
   (ComponentName :key1 val1 :key2 val2 child1 child2 ...)

2. Primitives:
   - Strings: Double-quoted, e.g., "Hello". Escapes: \n, \t, \\, \".
   - Numbers: Integers or decimals, e.g., 42 or 3.14.
   - Booleans: true or false.
   - Null: null.

3. Property Arguments:
   - Tagged attributes: Prefixed with a colon ':', e.g., :align "stretch" or :variant "body". Tagged keys are order-independent.
   - Positional attributes: Can be passed sequentially matching catalog signature order.

4. Child Components:
   - Nested parenthesized expressions without a property key are treated as children of the component, e.g., (Card (Column (Text "Hello"))).

5. Data Bindings:
   - Absolute data model paths start with '$/', e.g., $/user/firstName.
   - Relative list paths start with '$', e.g., $name.

6. Data Model Population:
   - Initialize data values using (data $/key "value" $/key2 123) or (set! $/key "value").

7. Dynamic List Templates:
   - List templates use (template :item item (Card (Text item/name))).

8. Action Events:
   - Actions use (Event "action_name" :param1 $/value).

9. Standalone Operations:
   - Delete surface: (deleteSurface "surface_id")
   - Call RPC function: (callFunction "openUrl" :url "https://example.com")
'''


class AtomPromptGenerator(PromptGenerator):
    """Generates catalog prompts for Atom S-Expression format."""

    def __init__(self, format_inst: "AtomFormat"):
        self.format = format_inst
        try:
            from a2ui.inference_formats.experimental.express.schema_helper import CatalogSchemaHelper
            self.schema_helper = CatalogSchemaHelper(format_inst.catalog)
        except Exception:
            self.schema_helper = None

    def generate_system_prompt(
        self, client_capabilities: Optional[V09Capabilities] = None
    ) -> str:
        """Generates system prompt for Atom format."""
        prompt = [ATOM_RULES, "\n## Component Catalog Signatures\n"]
        for comp_name in sorted(self.schema_helper.get_all_component_names()):
            sig = self._get_component_signature(comp_name)
            prompt.append(f"- {sig}")

        if self.format.examples_path:
            examples = self.get_examples(self.format.examples_path)
            if examples:
                prompt.append("\n## Examples\n")
                prompt.append(examples)

        return "\n".join(prompt)

    def _get_component_signature(self, comp_name: str) -> str:
        """Generates S-expression signature string for a component."""
        props = self.schema_helper.get_component_properties(comp_name)
        params = []
        for prop_name, prop_schema in props.items():
            if prop_name in ("id", "component"):
                continue
            is_req = self.schema_helper.is_property_required(comp_name, prop_name)
            params.append(f":{prop_name}" if is_req else f"[:{prop_name}]")
        return f"({comp_name} {' '.join(params)})"
