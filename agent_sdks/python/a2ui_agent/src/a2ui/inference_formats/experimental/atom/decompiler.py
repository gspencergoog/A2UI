# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Decompilation engine for A2UI Atom format."""

import json
from typing import Any, Dict, List, Union, Optional
from a2ui.core.catalog import Catalog
from a2ui.schema.catalog import A2uiCatalog


class AtomDecompiler:
    """Decompiles A2UI JSON payloads back into clean Atom S-Expressions."""

    def __init__(self, catalog: Optional[Union[Catalog[Any, Any], A2uiCatalog]] = None):
        self.catalog = catalog

    def decompile(self, payload: Dict[str, Any]) -> str:
        """Decompiles payload dictionary into Atom syntax string."""
        if "deleteSurface" in payload:
            surf_id = payload["deleteSurface"].get("surfaceId", "main")
            return f'(deleteSurface "{surf_id}")'

        if "callFunction" in payload:
            call_obj = payload["callFunction"]
            func_name = call_obj.get("call", "")
            args = call_obj.get("args", {})
            args_str = " ".join([f':{k} {self._format_val(v)}' for k, v in args.items()])
            return f'(callFunction "{func_name}" {args_str})'.strip()

        if "updateDataModel" in payload:
            val_obj = payload["updateDataModel"].get("value", {})
            data_pairs = " ".join([f'$/{k} {self._format_val(v)}' for k, v in val_obj.items()])
            return f'(data {data_pairs})'

        if "createSurface" in payload:
            surface_obj = payload["createSurface"]
            components = surface_obj.get("components", [])
            data_model = surface_obj.get("dataModel", {})

            lines = []
            if data_model:
                pairs = " ".join([f'$/{k} {self._format_val(v)}' for k, v in data_model.items()])
                lines.append(f'(data {pairs})\n')

            if components:
                # Map component ID to object
                comp_map = {c["id"]: c for c in components}
                # Find root component (first node not referenced as a child, or node_0)
                all_children = set()
                for c in components:
                    if "child" in c:
                        all_children.add(c["child"])
                    if "children" in c:
                        all_children.update(c["children"])
                
                root_id = components[0]["id"]
                for c in components:
                    if c["id"] not in all_children:
                        root_id = c["id"]
                        break

                lines.append(self._decompile_component(root_id, comp_map, indent=0))

            return "\n".join(lines)

        return ""

    def _decompile_component(self, comp_id: str, comp_map: Dict[str, Any], indent: int = 0) -> str:
        if comp_id not in comp_map:
            return ""

        comp = comp_map[comp_id]
        comp_type = comp.get("component", "View")
        pad = "  " * indent

        props = []
        for k, v in comp.items():
            if k in ("id", "component", "child", "children"):
                continue
            props.append(f':{k} {self._format_val(v)}')

        props_str = " " + " ".join(props) if props else ""

        # Decompile children
        child_nodes = []
        if "child" in comp:
            child_nodes.append(self._decompile_component(comp["child"], comp_map, indent + 1))
        elif "children" in comp:
            for child_id in comp["children"]:
                child_nodes.append(self._decompile_component(child_id, comp_map, indent + 1))

        if not child_nodes:
            return f"{pad}({comp_type}{props_str})"

        children_str = "\n" + "\n".join(child_nodes)
        return f"{pad}({comp_type}{props_str}{children_str})"

    def _format_val(self, val: Any) -> str:
        if isinstance(val, bool):
            return "true" if val else "false"
        if val is None:
            return "null"
        if isinstance(val, dict):
            if "path" in val:
                path = val["path"]
                return f"$/{path}" if not path.startswith("/") and not path.startswith("$") else path
            if "event" in val:
                evt = val["event"]
                ctx = val.get("context", {})
                ctx_str = " " + " ".join([f":{k} {self._format_val(v)}" for k, v in ctx.items()]) if ctx else ""
                return f'(Event "{evt}"{ctx_str})'
        if isinstance(val, str):
            return f'"{val}"'
        return str(val)

    def wrap_decompiled_blocks(self, blocks: List[str]) -> str:
        return "<a2ui>\n" + "\n\n".join(blocks) + "\n</a2ui>"
