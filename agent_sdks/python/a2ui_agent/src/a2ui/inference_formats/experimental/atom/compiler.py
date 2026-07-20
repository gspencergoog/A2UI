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

"""Compilation engine for A2UI Atom S-Expressions."""

import re
import json
from typing import Any, Dict, List, Tuple, Union, Optional
from a2ui.core.catalog import Catalog
from a2ui.schema.catalog import A2uiCatalog
class CatalogSchemaHelperWrapper:
    def __init__(self, catalog: Any):
        self.catalog = catalog

    def get_component_properties(self, comp_type: str) -> Dict[str, Any]:
        if hasattr(self.catalog, "get_components"):
            comps = self.catalog.get_components()
            if comp_type in comps:
                return comps[comp_type].get("properties", {})
        try:
            from a2ui.inference_formats.experimental.express.schema_helper import CatalogSchemaHelper
            return CatalogSchemaHelper(self.catalog).get_component_properties(comp_type)
        except Exception:
            return {}


class SExprParser:
    """Tokenizer and S-expression AST parser for Atom syntax."""

    def __init__(self, text: str):
        self.text = text
        self.tokens = self._tokenize(text)
        self.pos = 0

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizes S-expression string handling parens, brackets, quotes, keywords, and paths."""
        token_spec = [
            ("STRING", r'"(?:\\.|[^"\\])*"'),
            ("LPAREN", r'[(\[]'),
            ("RPAREN", r'[\])]'),
            ("KEYWORD", r':\w+'),
            ("PATH", r'\$/?[\w/]+'),
            ("SYMBOL", r'[^\s()":\[\],]+'),
            ("SKIP", r'[,\s]+'),
        ]
        tok_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_spec)
        tokens = []
        for mo in re.finditer(tok_regex, text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == "SKIP":
                continue
            tokens.append(value)
        return tokens

    def parse(self) -> List[Any]:
        """Parses tokens into nested S-expression lists."""
        expressions = []
        while self.pos < len(self.tokens):
            expr = self._parse_expr()
            if expr is not None:
                expressions.append(expr)
        return expressions

    def _parse_expr(self) -> Any:
        if self.pos >= len(self.tokens):
            return None

        tok = self.tokens[self.pos]
        if tok == "(":
            self.pos += 1
            elements = []
            while self.pos < len(self.tokens) and self.tokens[self.pos] != ")":
                sub = self._parse_expr()
                if sub is not None:
                    elements.append(sub)
            if self.pos < len(self.tokens) and self.tokens[self.pos] == ")":
                self.pos += 1
            # Auto-healing: If ')' is missing at EOF, return elements cleanly
            return elements
        elif tok == ")":
            self.pos += 1
            return None
        else:
            self.pos += 1
            return self._parse_atom(tok)

    def _parse_atom(self, tok: str) -> Any:
        if tok.startswith('"') and tok.endswith('"'):
            return tok[1:-1].encode().decode('unicode_escape')
        if tok == "true":
            return True
        if tok == "false":
            return False
        if tok == "null":
            return None
        try:
            if "." in tok:
                return float(tok)
            return int(tok)
        except ValueError:
            return tok


class AtomCompiler:
    """Compiles Atom S-Expression AST into standard A2UI v1.0 JSON payloads."""

    def __init__(self, catalog: Union[Catalog[Any, Any], A2uiCatalog, Any]):
        self.catalog = catalog
        self.schema_helper = CatalogSchemaHelperWrapper(catalog)
        self.node_counter = 0

    def _next_id(self) -> str:
        id_str = f"node_{self.node_counter}"
        self.node_counter += 1
        return id_str

    def _is_component_type(self, name: str) -> bool:
        """Determines if a string is a valid component type name."""
        if not name or not isinstance(name, str):
            return False
        if name in ("Card", "Column", "Row", "Text", "Image", "Icon", "Button", "List", "TextField", "ChoicePicker", "Divider", "Container", "Page"):
            return True
        if name[0].isupper():
            return True
        comp_props = self.schema_helper.get_component_properties(name)
        return bool(comp_props)

    def compile(
        self, text: str, surface_id: str = "main", is_final: bool = True
    ) -> Dict[str, Any]:
        """Compiles raw Atom text into an A2UI message dictionary."""
        parser = SExprParser(text)
        exprs = parser.parse()
        if not exprs:
            raise ValueError("No valid Atom expressions found.")

        data_model: Dict[str, Any] = {}
        components: List[Dict[str, Any]] = []

        for expr in exprs:
            if not isinstance(expr, list) or not expr:
                continue

            head = str(expr[0])

            if head in ("data", "set!"):
                self._parse_data_node(expr, data_model)
            elif head == "deleteSurface":
                surface_target = str(expr[1]) if len(expr) > 1 else surface_id
                return {
                    "version": "v1.0",
                    "deleteSurface": {"surfaceId": surface_target},
                }
            elif head == "callFunction":
                func_name = str(expr[1]) if len(expr) > 1 else ""
                args = {}
                i = 2
                while i < len(expr):
                    tok = str(expr[i])
                    if tok.startswith(":") and i + 1 < len(expr):
                        args[tok[1:]] = expr[i + 1]
                        i += 2
                    else:
                        i += 1
                return {
                    "version": "v1.0",
                    "callFunction": {
                        "call": func_name,
                        "args": args,
                    },
                }
            elif head in ("createSurface", "surface"):
                for sub in expr[1:]:
                    if isinstance(sub, list) and sub:
                        if str(sub[0]) in ("data", "set!"):
                            self._parse_data_node(sub, data_model)
                        elif self._is_component_type(str(sub[0])):
                            self._compile_component(sub, components, data_model, is_root=True)
            else:
                # Component root tree
                root_id = self._compile_component(expr, components, data_model, is_root=True)

        if not components and data_model:
            return {
                "version": "v1.0",
                "updateDataModel": {
                    "surfaceId": surface_id,
                    "path": "/",
                    "value": data_model,
                },
            }

        return {
            "version": "v1.0",
            "createSurface": {
                "surfaceId": surface_id,
                "catalogId": getattr(self.catalog, "id", "basic"),
                "components": components,
                "dataModel": data_model,
            },
        }

    def _parse_data_node(self, expr: List[Any], data_model: Dict[str, Any]) -> None:
        """Parses (data $/path/key val ...) into data_model structure."""
        head = str(expr[0])
        pairs = []
        if head == "data":
            i = 1
            while i < len(expr) - 1:
                pairs.append((str(expr[i]), expr[i + 1]))
                i += 2
        elif head == "set!" and len(expr) >= 3:
            pairs.append((str(expr[1]), expr[2]))

        for k, v in pairs:
            clean_path = k[2:] if k.startswith("$/") else k
            clean_path = clean_path.lstrip("/")
            if not clean_path:
                continue
            parts = clean_path.split("/")
            curr = data_model
            for p in parts[:-1]:
                if p not in curr or not isinstance(curr[p], dict):
                    curr[p] = {}
                curr = curr[p]
            curr[parts[-1]] = v

    def _compile_component(
        self,
        expr: List[Any],
        components: List[Dict[str, Any]],
        data_model: Optional[Dict[str, Any]] = None,
        is_root: bool = False,
    ) -> str:
        """Recursively processes S-expression component nodes into flat JSON adjacency list."""
        if data_model is None:
            data_model = {}
        comp_type = str(expr[0])
        comp_id = "root" if is_root else self._next_id()
        comp_dict: Dict[str, Any] = {"id": comp_id, "component": comp_type}

        children: List[str] = []
        i = 1
        pos_arg_index = 0
        comp_props = self.schema_helper.get_component_properties(comp_type)
        if isinstance(comp_props, dict):
            prop_keys = [k for k in comp_props.keys() if k not in ("id", "component")]
        elif isinstance(comp_props, (list, tuple)):
            prop_keys = [k for k in comp_props if k not in ("id", "component")]
        else:
            prop_keys = []

        while i < len(expr):
            item = expr[i]
            if isinstance(item, str) and item.startswith(":"):
                # Tagged keyword attribute :key val
                key = item[1:]
                val = expr[i + 1] if i + 1 < len(expr) else None
                if key == "children" and isinstance(val, list):
                    for child_item in val:
                        if isinstance(child_item, list):
                            child_id = self._compile_component(child_item, components, data_model)
                            children.append(child_id)
                        elif isinstance(child_item, str):
                            children.append(child_item)
                elif key == "child" and isinstance(val, list):
                    child_id = self._compile_component(val, components, data_model)
                    comp_dict["child"] = child_id
                else:
                    comp_dict[key] = self._resolve_val(val, components)
                i += 2
            elif isinstance(item, list):
                # Nested child component or expression
                if item and str(item[0]) in ("data", "set!"):
                    self._parse_data_node(item, data_model)
                elif item and str(item[0]) == "Event":
                    # Inline (Event "action_name")
                    comp_dict["action"] = self._compile_event(item)
                elif item and str(item[0]) == "template":
                    # Inline template
                    comp_dict["template"] = self._compile_template(item, components)
                elif item and self._is_component_type(str(item[0])):
                    child_id = self._compile_component(item, components, data_model)
                    children.append(child_id)
                else:
                    # Flatten list of child component IDs or primitives
                    for sub_c in item:
                        if isinstance(sub_c, list) and sub_c and self._is_component_type(str(sub_c[0])):
                            child_id = self._compile_component(sub_c, components, data_model)
                            children.append(child_id)
                        elif isinstance(sub_c, str):
                            if sub_c not in ("]", ")", "[", "("):
                                children.append(sub_c)
                i += 1
            else:
                # Positional attribute matching schema definition order
                if comp_type in ("Column", "Row", "List", "Container", "Page"):
                    if isinstance(item, str) and item not in ("]", ")", "[", "("):
                        children.append(item)
                else:
                    if pos_arg_index < len(prop_keys):
                        pkey = prop_keys[pos_arg_index]
                        comp_dict[pkey] = self._resolve_val(item, components)
                        pos_arg_index += 1
                i += 1

        if children:
            if len(children) == 1 and self._schema_expects_single_child(comp_type):
                comp_dict["child"] = children[0]
            else:
                comp_dict["children"] = children

        components.insert(0, comp_dict)
        return comp_id

    def _resolve_val(self, val: Any, components: List[Dict[str, Any]]) -> Any:
        """Resolves primitive values, dynamic bindings, and helper expressions."""
        if isinstance(val, str):
            if val.startswith("$/"):
                return {"path": val[1:]}
            elif val.startswith("$"):
                return {"path": val}
        if isinstance(val, list) and val:
            head = str(val[0])
            if head == "Event":
                return self._compile_event(val)
            elif head in ("formatDate", "formatString", "formatCurrency"):
                return {
                    "call": head,
                    "args": {f"arg_{k}": self._resolve_val(v, components) for k, v in enumerate(val[1:])},
                }
        return val

    def _compile_event(self, expr: List[Any]) -> Dict[str, Any]:
        event_name = str(expr[1]) if len(expr) > 1 else ""
        context = {}
        i = 2
        while i < len(expr):
            if str(expr[i]).startswith(":") and i + 1 < len(expr):
                context[str(expr[i])[1:]] = expr[i + 1]
                i += 2
            else:
                i += 1
        ev_obj: Dict[str, Any] = {"name": event_name}
        if context:
            ev_obj["context"] = {k: self._resolve_val(v, []) for k, v in context.items()}
        return {"event": ev_obj}

    def _compile_template(self, expr: List[Any], components: List[Dict[str, Any]]) -> Dict[str, Any]:
        # (template :item item_var child_expr)
        template_child_id = ""
        for item in expr[1:]:
            if isinstance(item, list):
                template_child_id = self._compile_component(item, components)
        return {"componentId": template_child_id}

    def _schema_expects_single_child(self, comp_type: str) -> bool:
        props = self.schema_helper.get_component_properties(comp_type)
        return "child" in props and "children" not in props
