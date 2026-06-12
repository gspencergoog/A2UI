"""Prompt compiler for A2UI Express.

Compiles standard JSON catalog schemas into compact plain-text signatures and
instruction blocks for on-device models (e.g., Gemma 4).
"""

from typing import Optional
try:
    # pylint: disable=relative-beyond-top-level
    from .schema_helper import CatalogSchemaHelper
except (ImportError, ValueError):
    from schema_helper import CatalogSchemaHelper


class ExpressPromptGenerator:
    def __init__(self, catalog_path: str, feature_mask: Optional[set[str]] = None):
        self.helper = CatalogSchemaHelper(catalog_path, feature_mask=feature_mask)
        self.feature_mask = feature_mask

    def generate_component_signatures(self) -> str:
        signatures = []
        for name in sorted(self.helper.component_properties.keys()):
            props = self.helper.get_component_properties(name)
            reqs = self.helper.get_component_required(name)
            comp_schema = self.helper.components.get(name, {})
            ordered_args = []
            param_docs = []
            
            sub_schemas = [comp_schema]
            if "allOf" in comp_schema: sub_schemas.extend(comp_schema["allOf"])
            
            for p in props:
                is_req = p in reqs
                opt_suffix = "" if is_req else "?"
                ordered_args.append(f"{p}{opt_suffix}")
                prop_def = {}
                for sub in sub_schemas:
                    if "properties" in sub and p in sub["properties"]:
                        prop_def = sub["properties"][p]
                        break
                p_desc = prop_def.get("description", "").strip()
                if p_desc:
                    param_docs.append(f"  - {p}: {p_desc.split(chr(10))[0]}")
                    
            sig = [f"• ({name} {' '.join(ordered_args)})"]
            desc = ""
            for sub in sub_schemas:
                d = sub.get("description", "").strip()
                if d:
                    desc = d
                    break
            if desc: sig.append(f"  {desc.split(chr(10))[0]}")
            if param_docs: sig.extend(param_docs)
            signatures.append("\n".join(sig))
        return "\n\n".join(signatures)

    def generate_function_signatures(self) -> str:
        signatures = []
        for name in sorted(self.helper.function_properties.keys()):
            props = self.helper.get_function_properties(name)
            reqs = self.helper.get_function_required(name)
            func_schema = self.helper.functions.get(name, {})
            ordered_args = []
            param_docs = []
            
            args_obj = func_schema.get("properties", {}).get("args", {}).get("properties", {})
            for p in props:
                is_req = p in reqs
                opt_suffix = "" if is_req else "?"
                ordered_args.append(f"{p}{opt_suffix}")
                prop_def = args_obj.get(p, {})
                p_desc = prop_def.get("description", "").strip()
                if p_desc:
                    param_docs.append(f"  - {p}: {p_desc.split(chr(10))[0]}")
                    
            sig = [f"• ({name} {' '.join(ordered_args)})"]
            desc = func_schema.get("description", "").strip()
            if desc: sig.append(f"  {desc.split(chr(10))[0]}")
            if param_docs: sig.extend(param_docs)
            signatures.append("\n".join(sig))
        return "\n\n".join(signatures)

    def generate_prompt(self) -> str:
        comp_sigs = self.generate_component_signatures()
        func_sigs = self.generate_function_signatures()

        return f"""# A2UI Express DSL

Use compact S-expression syntax inside <a2ui>...</a2ui>. Omit structural keys and trailing nulls.

## Grammar Rules
1. S-expressions: (Component arg1 arg2)
2. Arrays: [item1 item2]
3. Maps: {{key1 val1 key2 val2}} (no colons)
4. Primitives: "string", 42, true, false, ~ (null). Unquoted lowercase words allowed for strings.
5. Paths: @/absolute/path or @relativePath
6. Checks: ?rule or (?rule arg1)
7. Events: (!event_name) or (!event_name {{ctx_key ctx_val}})
8. Data init: (= @/path value)

The first evaluated component is the root. Do NOT use variables; auto-generate IDs via nesting.

## Component Signatures
{comp_sigs}

## Function Signatures
{func_sigs}

## Example
```
<a2ui>
(= @/form/rep "John Doe")
(= @/form/value 1500.00)
(Column [(TextField "Representative" @/form/rep "Enter name") (TextField "Deal Value" @/form/value "0.00" number ?required)])
</a2ui>
```
"""