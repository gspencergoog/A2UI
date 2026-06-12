"""Decompilation engine for A2UI Express.

Reconstructs standard A2UI v1.0 JSON envelopes back into A2UI Express DSL code,
tailored for prompt tokens compression.
"""

import re
from typing import Any
try:
    # pylint: disable=relative-beyond-top-level
    from .schema_helper import CatalogSchemaHelper
except (ImportError, ValueError):
    from schema_helper import CatalogSchemaHelper


def _flatten_data_model(data_dict: dict) -> list[tuple[str, Any]]:
    """Flattens a nested dictionary dataModel structure into JSON Pointer path segments."""
    results = []
    def recurse(current: Any, path: str):
        if isinstance(current, dict) and current:
            for k, v in current.items():
                recurse(v, f"{path}/{k}")
        else:
            results.append((path, current))
    recurse(data_dict, "")
    return results


class ExpressDecompiler:
    def __init__(self, catalog_path: str):
        self.helper = CatalogSchemaHelper(catalog_path)

    def decompile(self, envelope_json: dict) -> str:
        create_surface = envelope_json.get("createSurface", {})
        components = create_surface.get("components", [])
        data_model = create_surface.get("dataModel", {})

        dsl_lines = []
        
        if data_model:
            for path, val in sorted(_flatten_data_model(data_model)):
                val_str = self._decompile_value(val, {})
                dsl_lines.append(f"(= @{path} {val_str})")

        self.comp_by_id = {c["id"]: c for c in components}
        
        if "root" in self.comp_by_id:
            root_expr = self._decompile_component("root")
            dsl_lines.append(root_expr)

        return "\n".join(dsl_lines)

    def _decompile_component(self, comp_id: str) -> str:
        c = self.comp_by_id.get(comp_id)
        if not c:
            return comp_id
            
        comp_name = c["component"]
        properties = self.helper.get_component_properties(comp_name)
        args_reprs = []

        for prop_name in properties:
            if prop_name == "checks":
                checks_val = c.get("checks", [])
                if not checks_val:
                    args_reprs.append("~")
                    continue

                compiled_checks_list = []
                for rc in checks_val:
                    condition = rc.get("condition", {})
                    message = rc.get("message", "")
                    check_name = condition.get("call")
                    check_args = condition.get("args", {})
                    check_props = self.helper.get_function_properties(check_name)
                    
                    explicit_args_reprs = []
                    start_idx = 1 if (check_props and check_props[0] == "value") else 0
                    
                    for idx in range(start_idx, len(check_props)):
                        p = check_props[idx]
                        if p in check_args:
                            explicit_args_reprs.append(self._decompile_value(check_args[p], {}))

                    if message and message != f"{check_name.capitalize()} check failed":
                        explicit_args_reprs.append(f'"{message.replace(chr(34), chr(92)+chr(34))}"')

                    if explicit_args_reprs:
                        compiled_checks_list.append(f"(?{check_name} {' '.join(explicit_args_reprs)})")
                    else:
                        compiled_checks_list.append(f"?{check_name}")

                if len(compiled_checks_list) == 1:
                    args_reprs.append(compiled_checks_list[0])
                else:
                    args_reprs.append(f"[{' '.join(compiled_checks_list)}]")
                continue

            if prop_name in c:
                val = c[prop_name]
                if isinstance(val, str) and val in self.comp_by_id:
                    args_reprs.append(self._decompile_component(val))
                elif isinstance(val, list) and all(isinstance(x, str) and x in self.comp_by_id for x in val):
                    list_reprs = [self._decompile_component(x) for x in val]
                    args_reprs.append(f"[{' '.join(list_reprs)}]")
                else:
                    args_reprs.append(self._decompile_value(val, {}))
            else:
                args_reprs.append("~")

        while args_reprs and args_reprs[-1] == "~":
            args_reprs.pop()

        return f"({comp_name} {' '.join(args_reprs)})"

    def _decompile_value(self, val: Any, comp_ids: dict) -> str:
        if isinstance(val, dict):
            if "path" in val:
                if "componentId" in val:
                    path_repr = self._decompile_value({"path": val["path"]}, comp_ids)
                    comp_id_repr = val["componentId"]
                    return f"(Template {path_repr} {comp_id_repr})"
                path_str = val["path"]
                if path_str.startswith("/"): return f"@/{path_str[1:]}"
                return f"@{path_str}"

            if "event" in val:
                evt = val["event"]
                name = evt.get("name", "")
                ctx = evt.get("context", {})
                if ctx:
                    ctx_reprs = [f"{k} {self._decompile_value(v, comp_ids)}" for k, v in ctx.items()]
                    return f'(!{name} {{" ".join(ctx_reprs)}})'
                return f'(!{name})'

            if "functionCall" in val or "call" in val:
                fn = val.get("functionCall") or val
                name = fn["call"]
                args = fn.get("args", {})
                fn_props = self.helper.get_function_properties(name)
                args_reprs = []
                for p in fn_props:
                    if p in args:
                        args_reprs.append(self._decompile_value(args[p], comp_ids))
                    else:
                        args_reprs.append("~")
                while args_reprs and args_reprs[-1] == "~":
                    args_reprs.pop()
                return f"({name} {' '.join(args_reprs)})"

            items_reprs = [f"{k} {self._decompile_value(v, comp_ids)}" for k, v in val.items()]
            return f'{{ {" ".join(items_reprs)} }}'

        if isinstance(val, list):
            list_reprs = [self._decompile_value(item, comp_ids) for item in val]
            return f"[{' '.join(list_reprs)}]"

        if isinstance(val, str):
            if re.match(r'^[a-z_][a-z0-9_-]*$', val):
                return val
            escaped = val.replace('"', '\\"')
            return f'"{escaped}"'

        if isinstance(val, bool):
            return "true" if val else "false"

        if val is None:
            return "~"

        return str(val)
