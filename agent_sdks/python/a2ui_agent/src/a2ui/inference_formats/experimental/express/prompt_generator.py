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

"""Prompt compiler for A2UI Express.

Compiles standard JSON catalog schemas into compact plain-text signatures and
instruction blocks for on-device models (e.g., Gemma 4).
"""

import json
import re
from typing import Any, Optional, TYPE_CHECKING, Union
from a2ui.prompt import PromptGenerator
from a2ui.core.schema.client_capabilities import V09Capabilities

from .parser import ExpressParser
from .schema_helper import CatalogSchemaHelper


if TYPE_CHECKING:
    from .format import ExpressFormat

EXPRESS_RULES = r"""# A2UI Express Output Contract

Output the user interface using this DSL wrapped inside `<a2ui>` and `</a2ui>` sentinel tags. Do NOT output raw JSON.

## Grammar Rules

1. Assign every component to its own variable on a separate line:
   var_name = ComponentName(arg1, arg2, ...)
   Component constructors CANNOT be passed inline as positional arguments to other components.

2. UI surfaces must have a root component assigned to the reserved variable 'root'. For data-only updates (with no UI surface), output standalone data path assignments (e.g. $/user/name = "Alice") without a 'root' variable.

3. Data bindings:
   - Absolute data paths: $/user/firstName
   - Relative template paths: $firstName (or '$' for the item itself)

4. Logic & validation: Prefix client checks with '?', e.g., ?required or ?regex("^[0-9]{5}$", "Invalid code").

5. Action events: Represent actions using Event("name", {context_map}) or function calls like openUrl("https://example.com"). If an action property is required but no specific action is described, pass Event("click").

6. Data model population: Assign values directly to absolute data paths (e.g. $/user/name = "Alice"). Values can be primitives, arrays, or maps.

7. Dynamic list templates: Represent list templates using _template($/path/to/list, itemTemplate) and define itemTemplate on its own line.

8. Surface deletion: Output deleteSurface("surface-id") to delete a surface.

9. Static properties: Arguments annotated with '(static only)' MUST be defined as literal values or arrays inline (or as a local DSL variable representing a static structure). You CANNOT use a dynamic data binding path (prefixed by $) for these arguments."""


def _schema_allows_databinding(prop_schema: Any) -> bool:
    """Helper to check if a JSON schema allows data binding (DynamicString/DataBinding, etc)."""
    if not isinstance(prop_schema, dict):
        return False
    if "$ref" in prop_schema:
        ref = prop_schema["$ref"]
        if "DataBinding" in ref or "Dynamic" in ref or "ChildList" in ref:
            return True
    if "oneOf" in prop_schema or "anyOf" in prop_schema or "allOf" in prop_schema:
        subs = (
            prop_schema.get("oneOf", [])
            + prop_schema.get("anyOf", [])
            + prop_schema.get("allOf", [])
        )
        for sub in subs:
            if _schema_allows_databinding(sub):
                return True
    return False


def _get_schema_enum(prop_schema: Any) -> Optional[list[str]]:
    """Helper to recursively find enum definitions inside a JSON schema."""
    if not isinstance(prop_schema, dict):
        return None
    if "enum" in prop_schema:
        return prop_schema["enum"]
    if "oneOf" in prop_schema or "anyOf" in prop_schema:
        subs = prop_schema.get("oneOf", []) + prop_schema.get("anyOf", [])
        for sub in subs:
            enum_val = _get_schema_enum(sub)
            if enum_val:
                return enum_val
    return None


class ExpressPromptGenerator(PromptGenerator):
    """Generates system prompt contracts guiding models to produce A2UI Express.

    Compiles component catalog structures and logic helper catalogs into standard
    positional signatures, reducing prompt token utilization.
    """

    def __init__(self, format_inst: "ExpressFormat"):
        """Initializes the generator with the specified format.

        Args:
            format_inst: An ExpressFormat instance.
        """
        self._format = format_inst
        self.catalog = format_inst.catalog
        self.helper = CatalogSchemaHelper(format_inst.catalog)
        self.parser: Optional[ExpressParser] = None

    def generate_component_signatures(self) -> str:
        """Compiles component definitions into clean function-like signatures.

        Returns:
            A plain-text multi-line list of component signatures.
        """
        signatures = []
        for name in sorted(self.helper.component_properties.keys()):
            props = self.helper.get_component_properties(name)
            reqs = self.helper.get_component_required(name)

            # Retrieve component-level description
            comp_desc = self.helper.get_component_description(name)

            ordered_args = []
            prop_details = []
            for p in props:
                is_req = p in reqs
                opt_suffix = "" if is_req else "?"

                p_schema = self.helper.get_property_schema(name, p)

                # Determine signature argument label
                arg_label = f"{p}{opt_suffix}"

                is_component_id = False
                if isinstance(p_schema, dict) and "$ref" in p_schema:
                    if "ComponentId" in p_schema["$ref"]:
                        is_component_id = True

                if is_component_id:
                    arg_label += " (component ID)"
                elif not _schema_allows_databinding(p_schema):
                    arg_label += " (static only)"

                ordered_args.append(arg_label)

                # Retrieve parameter description
                p_desc = (
                    p_schema.get("description") if isinstance(p_schema, dict) else None
                )
                enum_vals = _get_schema_enum(p_schema)

                # Build property detail description
                if p_desc or enum_vals:
                    p_line_parts = []
                    if p_desc:
                        p_line_parts.append(p_desc)
                    if enum_vals:
                        enum_vals_str = ", ".join([f"'{v}'" for v in enum_vals])
                        p_line_parts.append(f"Must be one of: {enum_vals_str}")
                    prop_details.append(f"  - {p}: {' '.join(p_line_parts)}")

                # Fetch property schema and check if it has nested object structure
                if isinstance(p_schema, dict):
                    if p_schema.get("type") == "object" and "properties" in p_schema:
                        sub_keys = []
                        for sub_k, sub_v in p_schema["properties"].items():
                            desc = sub_v.get("description", "")
                            desc_suffix = f" - {desc}" if desc else ""
                            sub_keys.append(f"    * {sub_k}{desc_suffix}")

                        if prop_details and prop_details[-1].startswith(f"  - {p}:"):
                            prop_details[-1] += "\n    Map keys:\n" + "\n".join(
                                sub_keys
                            )
                        else:
                            prop_details.append(
                                f"  - {p}: Map with keys:\n" + "\n".join(sub_keys)
                            )
                    elif p_schema.get("type") == "array" and "items" in p_schema:
                        items_schema = p_schema["items"]
                        if (
                            isinstance(items_schema, dict)
                            and items_schema.get("type") == "object"
                            and "properties" in items_schema
                        ):
                            sub_keys = []
                            for sub_k, sub_v in items_schema["properties"].items():
                                desc = sub_v.get("description", "")
                                desc_suffix = f" - {desc}" if desc else ""
                                sub_keys.append(f"    * {sub_k}{desc_suffix}")

                            if prop_details and prop_details[-1].startswith(
                                f"  - {p}:"
                            ):
                                prop_details[
                                    -1
                                ] += "\n    List of maps keys:\n" + "\n".join(sub_keys)
                            else:
                                prop_details.append(
                                    f"  - {p}: List of maps with keys:\n"
                                    + "\n".join(sub_keys)
                                )

            sig = f"• {name}({', '.join(ordered_args)})"
            if comp_desc:
                sig += f"\n  - Description: {comp_desc}"
            if prop_details:
                sig += "\n" + "\n".join(prop_details)
            signatures.append(sig)
        return "\n".join(signatures)

    def generate_function_signatures(self) -> str:
        """Compiles function definitions into clean signatures.

        Returns:
            A plain-text multi-line list of function signatures.
        """
        signatures = []
        for name in sorted(self.helper.function_properties.keys()):
            props = self.helper.get_function_properties(name)
            reqs = self.helper.get_function_required(name)

            # Retrieve function-level description
            f_desc = self.helper.get_function_description(name)

            ordered_args = []
            prop_details = []

            func_schema = self.helper.functions.get(name, {})
            args_properties = (
                func_schema.get("properties", {}).get("args", {}).get("properties", {})
            )

            for p in props:
                is_req = p in reqs
                opt_suffix = "" if is_req else "?"
                ordered_args.append(f"{p}{opt_suffix}")

                p_schema = args_properties.get(p, {})
                p_desc = (
                    p_schema.get("description") if isinstance(p_schema, dict) else None
                )
                if p_desc:
                    prop_details.append(f"  - {p}: {p_desc}")

            sig = f"• {name}({', '.join(ordered_args)})"
            if f_desc:
                sig += f"\n  - Description: {f_desc}"
            if prop_details:
                sig += "\n" + "\n".join(prop_details)
            signatures.append(sig)
        return "\n".join(signatures)

    def _build_schema_prompt(self) -> str:
        return self.catalog_description(include_schema=True)

    def catalog_description(self, include_schema: bool = True) -> str:
        """Assembles the system prompt component catalog signatures block.

        Args:
            include_schema: Whether to include the schema description.

        Returns:
            The rendered LLM instructions string block containing positional signatures.
        """
        if not include_schema:
            return ""

        comp_sigs = self.generate_component_signatures()
        func_sigs = self.generate_function_signatures()
        catalog_instructions = (
            self.helper.catalog.get("instructions", "") if self.helper else ""
        )

        # Translate json examples in catalog instructions into A2UI Express DSL
        if catalog_instructions:
            pattern = r"```json\s*\n(.*?)\n```"
            catalog_instructions = re.sub(
                pattern,
                self._replace_json_block_in_instructions,
                catalog_instructions,
                flags=re.DOTALL,
            )

        # Format catalog instructions block if it exists
        catalog_instructions_block = ""
        if catalog_instructions:
            catalog_instructions_block = (
                f"\n\n## Catalog Instructions\n\n{catalog_instructions}"
            )

        desc = (
            "## Positional Component Signatures\n\nUse these exact positional"
            " signatures to instantiate components. Do not output property"
            f" keys:\n{comp_sigs}\n\n## Positional Function Signatures\n\nUse these"
            " exact positional signatures to instantiate check rules or logic"
            f" functions:\n{func_sigs}{catalog_instructions_block}"
        )
        return desc

    def decompile(self, val: dict[str, Any]) -> str:
        """Decompiles a structured JSON surface block into Express DSL.

        Args:
            val: The structured JSON dictionary representing surface instructions.

        Returns:
            The Express DSL string representation of the surface.
        """
        parser = self.parser or self._format.parser
        if not parser:
            self._format._ensure_catalog()
            parser = self._format.parser
            assert parser is not None
        return parser.decompile(val)

    def wrap_decompiled_blocks(self, blocks: list[str]) -> str:
        """Encloses decompiled DSL code blocks in markdown code fences and sentinel tags.

        Args:
            blocks: A list of Express DSL snippet strings.

        Returns:
            The enclosed and formatted markdown block.
        """
        parser = self.parser or self._format.parser
        if not parser:
            self._format._ensure_catalog()
            parser = self._format.parser
            assert parser is not None
        return parser.wrap_decompiled_blocks(blocks)

    def _replace_json_block_in_instructions(self, match: re.Match[str]) -> str:
        json_content = match.group(1).strip()
        try:
            parsed = json.loads(json_content)
            if isinstance(parsed, dict):
                messages = [parsed]
            elif isinstance(parsed, list):
                messages = parsed
            else:
                return str(match.group(0))

            dsl_blocks = []
            for msg in messages:
                if isinstance(msg, dict) and any(
                    k in msg
                    for k in [
                        "createSurface",
                        "updateDataModel",
                        "deleteSurface",
                        "callFunction",
                    ]
                ):
                    dsl_clean = self.decompile(msg)
                    dsl_blocks.append(dsl_clean)
                else:
                    return str(match.group(0))

            full_dsl = self.wrap_decompiled_blocks(dsl_blocks)
            return f"```\n{full_dsl}\n```"
        except Exception:
            return str(match.group(0))

    def _replace_json_block(self, match: re.Match[str]) -> str:
        json_content = match.group(1).strip()
        try:
            parsed = json.loads(json_content)
            if isinstance(parsed, dict):
                messages = [parsed]
            elif isinstance(parsed, list):
                messages = parsed
            else:
                return str(match.group(0))

            blocks = []
            for msg in messages:
                if isinstance(msg, dict) and any(
                    k in msg
                    for k in [
                        "createSurface",
                        "updateDataModel",
                        "deleteSurface",
                        "callFunction",
                    ]
                ):
                    decompiled = self.decompile(msg)
                    blocks.append(decompiled)
                else:
                    return str(match.group(0))

            return self.wrap_decompiled_blocks(blocks)
        except Exception:
            return str(match.group(0))

    def transform_examples(self, raw_examples_markdown: str) -> str:
        """Transforms JSON blocks in raw markdown into Express DSL syntax."""
        if not self.catalog:
            return raw_examples_markdown

        triple_backticks = chr(96) * 3
        pattern = rf"{triple_backticks}json\s*\n(.*?)\n{triple_backticks}"

        return re.sub(
            pattern,
            self._replace_json_block,
            raw_examples_markdown,
            flags=re.DOTALL,
        )

    def generate(
        self,
        role_description: str,
        workflow_description: str = "",
        ui_description: str = "",
        client_ui_capabilities: Optional[Union[dict[str, Any], V09Capabilities]] = None,
        allowed_components: Optional[list[str]] = None,
        allowed_messages: Optional[list[str]] = None,
        include_schema: bool = False,
        include_examples: bool = False,
        validate_examples: bool = False,
    ) -> str:
        """Assembles the complete system instruction block for the LLM.

        Args:
            role_description: Description of the agent's role.
            workflow_description: Optional description of the task workflow.
            ui_description: Optional UI context or rules.
            client_ui_capabilities: Optional client UI capability details.
            allowed_components: Optional list of component tags the LLM may use.
            allowed_messages: Optional list of A2UI message types allowed.
            include_schema: Whether to include component schemas in the prompt.
            include_examples: Whether to include few-shot examples.
            validate_examples: Whether to validate few-shot examples on generation.

        Returns:
            The complete system prompt string explaining A2UI Express and its catalog.
        """
        catalog = self._format.catalog if self._format else None
        if catalog and (allowed_components or allowed_messages):
            catalog = catalog.with_pruning(allowed_components, allowed_messages)

        if self._format:
            self.helper = CatalogSchemaHelper(catalog) if catalog else None
            self.parser = ExpressParser(catalog) if catalog else None

        parts = [role_description]

        rules = EXPRESS_RULES
        if workflow_description:
            rules += f"\n\n{workflow_description}"
        parts.append(f"## Workflow Description:\n{rules}")

        if ui_description:
            parts.append(f"## UI Description:\n{ui_description}")

        if include_schema and self.helper:
            prompt = self._build_schema_prompt()
            parts.append(prompt)

        if include_examples and self._format and self._format.examples_path and catalog:
            raw_examples = catalog.load_examples(
                self._format.examples_path, validate=validate_examples
            )
            if raw_examples:
                formatted_examples = self.transform_examples(raw_examples)
                parts.append(f"### Examples:\n{formatted_examples}")

        return "\n\n".join(parts)
