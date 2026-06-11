"""Decompilation engine for A2UI Express.

Reconstructs standard A2UI v1.0 JSON envelopes back into A2UI Express DSL code,
tailored for prompt tokens compression.
"""

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
    """Converts standard A2UI wire JSON trees back into A2UI Express syntax.

    Identifies component definitions, event trigger actions, validation logic rules,
    and dynamic child templates, maps them positional-wise, and outputs plain text.

    Attributes:
        helper: A CatalogSchemaHelper loaded with the target catalog schema.
    """

    def __init__(self, catalog_path: str):
        """Initializes the decompiler with the specified catalog.

        Args:
            catalog_path: The absolute filesystem path to the catalog JSON file.
        """
        self.helper = CatalogSchemaHelper(catalog_path)

    def decompile(self, envelope_json: dict) -> str:
        """Decompiles standard A2UI wire JSON into clean A2UI Express lines.

        Args:
            envelope_json: The standard A2UI v1.0 JSON envelope.

        Returns:
            The decompiled A2UI Express DSL string.
        """
        create_surface = envelope_json.get("createSurface", {})
        components = create_surface.get("components", [])
        data_model = create_surface.get("dataModel", {})

        dsl_lines = []
        # Index components by ID for hierarchy mapping
        comp_ids = {c["id"] for c in components}

        # Decompile dataModel paths first
        if data_model:
            for path, val in sorted(_flatten_data_model(data_model)):
                val_str = self._decompile_value(val, comp_ids)
                dsl_lines.append(f"${path} = {val_str}")


        for c in components:
            comp_id = c["id"]
            comp_name = c["component"]
            if comp_name not in self.helper.components:
                continue

            properties = self.helper.get_component_properties(comp_name)
            args_reprs = []

            for prop_name in properties:
                if prop_name == "checks":
                    # Decompile checks
                    checks_val = c.get("checks", [])
                    if not checks_val:
                        args_reprs.append("null")
                        continue

                    compiled_checks_list = []
                    for rc in checks_val:
                        condition = rc.get("condition", {})
                        message = rc.get("message", "")

                        check_name = condition.get("call")
                        check_args = condition.get("args", {})

                        check_props = self.helper.get_function_properties(
                            check_name)
                        explicit_args_reprs = []

                        # If first property is value (implicitly bound), skip it
                        start_idx = 0
                        if check_props and check_props[0] == "value":
                            start_idx = 1

                        for idx in range(start_idx, len(check_props)):
                            p = check_props[idx]
                            if p in check_args:
                                explicit_args_reprs.append(
                                    self._decompile_value(
                                        check_args[p], comp_ids))

                        if message and message != f"{check_name.capitalize()} check failed":
                            escaped_msg = message.replace('"', '\\"')
                            explicit_args_reprs.append(f'"{escaped_msg}"')

                        if explicit_args_reprs:
                            compiled_checks_list.append(
                                f"?{check_name}({', '.join(explicit_args_reprs)})"
                            )
                        else:
                            compiled_checks_list.append(f"?{check_name}")

                    if len(compiled_checks_list) == 1:
                        args_reprs.append(compiled_checks_list[0])
                    else:
                        args_reprs.append(
                            f"[{', '.join(compiled_checks_list)}]")
                    continue

                # Map other regular properties
                if prop_name in c:
                    val = c[prop_name]
                    args_reprs.append(self._decompile_value(val, comp_ids))
                else:
                    args_reprs.append("null")

            # Strip trailing optional null arguments for readability
            while args_reprs and args_reprs[-1] == "null":
                args_reprs.pop()

            dsl_lines.append(
                f"{comp_id} = {comp_name}({', '.join(args_reprs)})")

        return "\n".join(dsl_lines)

    def _decompile_value(self, val: Any, comp_ids: set[str]) -> str:
        """Decompiles a single value node back to A2UI Express notation.

        Args:
            val: The JSON-serialized property value structure.
            comp_ids: A set of all component IDs registered in the surface context.

        Returns:
            A plain-text representation of the value.
        """
        if isinstance(val, dict):
            if "path" in val:
                if "componentId" in val:
                    path_repr = self._decompile_value({"path": val["path"]},
                                                      comp_ids)
                    comp_id_repr = val["componentId"]
                    return f"Template({path_repr}, {comp_id_repr})"
                # Decompile path: prefixed by $
                path_str = val["path"]
                if path_str.startswith("/"):
                    return f"$/{path_str[1:]}"
                return f"${path_str}"

            if "event" in val:
                # Decompile server event: Event("name", context)
                evt = val["event"]
                name = evt.get("name", "")
                ctx = evt.get("context", {})
                ctx_reprs = []
                for k, v in ctx.items():
                    ctx_reprs.append(
                        f"{k}: {self._decompile_value(v, comp_ids)}")
                if ctx_reprs:
                    return f'Event("{name}", {{{", ".join(ctx_reprs)}}})'
                return f'Event("{name}")'

            if "functionCall" in val:
                # Decompile local function action: FunctionName(args)
                fn = val["functionCall"]
                name = fn["call"]
                args = fn.get("args", {})

                fn_props = self.helper.get_function_properties(name)
                args_reprs = []
                for p in fn_props:
                    if p in args:
                        args_reprs.append(
                            self._decompile_value(args[p], comp_ids))
                    else:
                        args_reprs.append("null")

                while args_reprs and args_reprs[-1] == "null":
                    args_reprs.pop()
                return f"{name}({', '.join(args_reprs)})"

            if "call" in val:
                # Decompile dynamic functional expression: FunctionName(args)
                name = val["call"]
                args = val.get("args", {})
                fn_props = self.helper.get_function_properties(name)
                args_reprs = []
                for p in fn_props:
                    if p in args:
                        args_reprs.append(
                            self._decompile_value(args[p], comp_ids))
                    else:
                        args_reprs.append("null")

                while args_reprs and args_reprs[-1] == "null":
                    args_reprs.pop()
                return f"{name}({', '.join(args_reprs)})"

            # General dict
            items_reprs = []
            for k, v in val.items():
                items_reprs.append(
                    f"{k}: {self._decompile_value(v, comp_ids)}")
            return f'{{{", ".join(items_reprs)}}}'

        if isinstance(val, list):
            # Decompile array
            list_reprs = [
                self._decompile_value(item, comp_ids) for item in val
            ]
            return f"[{', '.join(list_reprs)}]"

        if isinstance(val, str):
            # If it matches a component ID reference, keep it as a variable identifier
            # (if it is a structural variable name)
            if val in comp_ids:
                return val
            # Otherwise quote as string literal
            escaped = val.replace('"', '\\"')
            return f'"{escaped}"'

        if isinstance(val, bool):
            return "true" if val else "false"

        if val is None:
            return "null"

        return str(val)
