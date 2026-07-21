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
        try:
            from a2ui.inference_formats.experimental.express.schema_helper import CatalogSchemaHelper
            self._helper = CatalogSchemaHelper(self.catalog)
        except Exception:
            self._helper = None

    def get_component_properties(self, comp_type: str) -> Any:
        if self._helper:
            return self._helper.get_component_properties(comp_type)
        if hasattr(self.catalog, "get_components"):
            comps = self.catalog.get_components()
            if comp_type in comps:
                return comps[comp_type].get("properties", {})
        return {}

    def get_component_required(self, comp_type: str) -> list[str]:
        if self._helper:
            return self._helper.get_component_required(comp_type)
        return []

    def get_property_type(self, comp_type: str, prop_name: str) -> Optional[str]:
        if self._helper:
            return self._helper.get_property_type(comp_type, prop_name)
        return None


class SExprParser:
    """Tokenizer and S-expression AST parser for Atom syntax."""

    def __init__(self, text: str):
        self.text = text
        self.tokens = self._tokenize(text)
        self.pos = 0

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizes S-expression string handling parens, brackets, quotes, keywords, comments, and paths."""
        token_spec = [
            ("COMMENT", r';[^\n]*'),
            ("STRING", r'"(?:\\.|[^"\\])*"'),
            ("LPAREN", r'[(\[]'),
            ("RPAREN", r'[\])]'),
            ("KEYWORD_VAL", r':\w+=[^\s()":\[\],]+'),
            ("KEYWORD", r':\w+:?'),
            ("PATH", r'\$/?[\w/]+'),
            ("SYMBOL", r'[^\s()":\[\],]+'),
            ("SKIP", r'[,\s]+'),
        ]
        tok_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_spec)
        tokens = []
        for mo in re.finditer(tok_regex, text):
            kind = mo.lastgroup
            value = mo.group()
            if kind in ("SKIP", "COMMENT"):
                continue
            if kind == "KEYWORD_VAL":
                k, v = value.split("=", 1)
                tokens.append(k)
                tokens.append(v)
            elif kind == "KEYWORD":
                tokens.append(value.rstrip(":"))
            else:
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
        if tok in ("(", "[", "{"):
            closing = ")" if tok == "(" else ("]" if tok == "[" else "}")
            self.pos += 1
            elements = []
            while self.pos < len(self.tokens) and self.tokens[self.pos] != closing:
                sub = self._parse_expr()
                if sub is not None:
                    elements.append(sub)
            if self.pos < len(self.tokens) and self.tokens[self.pos] == closing:
                self.pos += 1
            return elements
        elif tok in (")", "]", "}"):
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
        # Filter out common English prose words starting with uppercase
        if name in ("Component", "NYC", "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "This", "The", "A", "An", "For", "With", "Both", "Although", "Note", "Here", "Inside", "Generate", "Create", "Update", "Delete"):
            return False
        comp_props = self.schema_helper.get_component_properties(name)
        if comp_props:
            return True
        if name[0].isupper() and name.isalnum() and not name.islower():
            return True
        return False

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
                i = 1
                while i < len(expr):
                    item = expr[i]
                    if isinstance(item, str) and item.startswith(":"):
                        val = expr[i + 1] if i + 1 < len(expr) else None
                        if item in (":id", ":surfaceId") and val:
                            surface_id = str(val)
                        elif item == ":data" and isinstance(val, list):
                            self._parse_data_node(val, data_model)
                        elif item in (":root", ":child", ":children", ":component") and isinstance(val, list):
                            if self._is_component_type(str(val[0])):
                                self._compile_component(val, components, data_model, is_root=True)
                            else:
                                for sub_elem in val:
                                    if isinstance(sub_elem, list) and sub_elem and self._is_component_type(str(sub_elem[0])):
                                        self._compile_component(sub_elem, components, data_model, is_root=True)
                        i += 2
                    elif isinstance(item, list) and item:
                        if str(item[0]) in ("data", "set!"):
                            self._parse_data_node(item, data_model)
                        elif self._is_component_type(str(item[0])):
                            self._compile_component(item, components, data_model, is_root=True)
                        i += 1
                    elif isinstance(item, str):
                        surface_id = item
                        i += 1
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

    def _clean_data_value(self, val: Any) -> Any:
        if isinstance(val, list):
            if not val:
                return []
            if len(val) >= 2 and len(val) % 2 == 0 and all(isinstance(val[i], str) for i in range(0, len(val), 2)):
                res = {}
                i = 0
                while i < len(val) - 1:
                    key = str(val[i]).lstrip(":")
                    res[key] = self._clean_data_value(val[i + 1])
                    i += 2
                return res
            return [self._clean_data_value(item) for item in val]
        if isinstance(val, dict):
            return {str(k).lstrip(":"): self._clean_data_value(v) for k, v in val.items()}
        return val

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
            clean_path = k[2:] if k.startswith("$/") else (k[1:] if k.startswith("$") else k)
            clean_path = clean_path.lstrip("/")
            if not clean_path:
                continue
            parts = clean_path.split("/")
            curr = data_model
            for p in parts[:-1]:
                if p not in curr or not isinstance(curr[p], dict):
                    curr[p] = {}
                curr = curr[p]
            curr[parts[-1]] = self._clean_data_value(v)

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
        comp_type = str(expr[0]).strip("`").strip("'")
        comp_id = "root" if is_root and not any(c.get("id") == "root" for c in components) else self._next_id()
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
                if (key == "children" or self.schema_helper.get_property_type(comp_type, key) == "ChildList") and isinstance(val, list):
                    if val and str(val[0]) == "template":
                        tmpl_data = self._compile_template(val, components)
                        if "items_path" in tmpl_data:
                            comp_dict["items"] = tmpl_data.pop("items_path")
                        comp_dict["template"] = tmpl_data
                    else:
                        for child_item in val:
                            if isinstance(child_item, list):
                                if child_item and str(child_item[0]) == "template":
                                    tmpl_data = self._compile_template(child_item, components)
                                    if "items_path" in tmpl_data:
                                        comp_dict["items"] = tmpl_data.pop("items_path")
                                    comp_dict["template"] = tmpl_data
                                else:
                                    child_id = self._compile_component(child_item, components, data_model)
                                    children.append(child_id)
                            elif isinstance(child_item, str) and child_item not in ("]", ")", "[", "("):
                                raise ValueError(
                                    f"Flat adjacency lists and string child ID references ('{child_item}') are disallowed in Atom format. "
                                    "Child components must be directly nested S-expressions."
                                )
                elif (self.schema_helper.get_property_type(comp_type, key) in ("Child", "ComponentId") or key in ("child", "trigger", "content", "header", "footer", "leading", "trailing")) and isinstance(val, list) and val and self._is_component_type(str(val[0])):
                    child_id = self._compile_component(val, components, data_model)
                    comp_dict[key] = child_id
                elif key == "tabs" and isinstance(val, list):
                    comp_dict["tabs"] = self._compile_tabs(val, components, data_model)
                elif key in ("template", "itemTemplate") and isinstance(val, list):
                    if val and str(val[0]) == "template":
                        tmpl_data = self._compile_template(val, components)
                    else:
                        child_id = self._compile_component(val, components, data_model)
                        tmpl_data = {"componentId": child_id}
                    if "items_path" in tmpl_data:
                        comp_dict["items"] = tmpl_data.pop("items_path")
                    comp_dict["template"] = tmpl_data
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
                    tmpl_data = self._compile_template(item, components)
                    if "items_path" in tmpl_data:
                        comp_dict["items"] = tmpl_data.pop("items_path")
                    comp_dict["template"] = tmpl_data
                elif item and self._is_component_type(str(item[0])):
                    child_id = self._compile_component(item, components, data_model)
                    children.append(child_id)
                else:
                    # Flatten list of child component IDs or primitives
                    for sub_c in item:
                        if isinstance(sub_c, list) and sub_c and self._is_component_type(str(sub_c[0])):
                            child_id = self._compile_component(sub_c, components, data_model)
                            children.append(child_id)
                        elif isinstance(sub_c, str) and sub_c not in ("]", ")", "[", "("):
                            if sub_c == "..." or sub_c.startswith("node_") or sub_c.startswith("child"):
                                continue
                            raise ValueError(
                                f"Flat adjacency lists and string child ID references ('{sub_c}') are disallowed in Atom format. "
                                "Child components must be directly nested S-expressions."
                            )
                i += 1
            else:
                # Positional attribute matching schema definition order
                if self.schema_helper.get_property_type(comp_type, "children") == "ChildList" or "children" in prop_keys or "child" in prop_keys:
                    if isinstance(item, str) and item not in ("]", ")", "[", "("):
                        raise ValueError(
                            f"Flat adjacency lists and string child ID references ('{item}') are disallowed in Atom format. "
                            "Child components must be directly nested S-expressions."
                        )
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

        if "template" in comp_dict and "items" not in comp_dict:
            found_path = None
            for k, v in data_model.items():
                if isinstance(v, list):
                    found_path = f"/{k}"
                    break
            comp_dict["items"] = {"path": found_path if found_path else "/items"}

        # Strict schema validation: required properties and enum constraints
        if hasattr(self.schema_helper, "get_component_required"):
            req_props = self.schema_helper.get_component_required(comp_type)
            for req in req_props:
                if req not in ("id", "component") and req not in comp_dict:
                    raise ValueError(
                        f"Component '{comp_type}' (id: '{comp_id}') is missing required property '{req}' "
                        f"defined by catalog schema."
                    )

        if hasattr(self.schema_helper, "_helper") and self.schema_helper._helper:
            for p_name, p_val in comp_dict.items():
                if p_name in ("id", "component", "children", "child"):
                    continue
                enum_vals = self.schema_helper._helper.get_property_enum(comp_type, p_name)
                if enum_vals and isinstance(p_val, str) and p_val not in enum_vals:
                    raise ValueError(
                        f"Invalid value '{p_val}' for property ':{p_name}' in component '{comp_type}'. "
                        f"Must be one of: {enum_vals}"
                    )

        components.insert(0, comp_dict)
        return comp_id

    def _resolve_val(self, val: Any, components: List[Dict[str, Any]]) -> Any:
        """Resolves primitive values, dynamic bindings, and helper expressions."""
        if isinstance(val, str):
            if val.startswith("$/"):
                return {"path": val[1:]}
            elif val.startswith("$"):
                return {"path": val}
            elif val.startswith("/"):
                return {"path": val}
            elif "/" in val and not val.startswith("http") and not val.startswith("https"):
                return {"path": f"/{val}" if not val.startswith("/") else val}
        if isinstance(val, list) and val:
            head = str(val[0])
            if head == "Event":
                return self._compile_event(val)
            elif head in ("formatDate", "formatString", "formatCurrency"):
                args_dict = {}
                i = 1
                arg_idx = 0
                while i < len(val):
                    item = val[i]
                    if isinstance(item, str) and item.startswith(":") and i + 1 < len(val):
                        args_dict[item[1:]] = self._resolve_val(val[i + 1], components)
                        i += 2
                    else:
                        args_dict[f"arg_{arg_idx}"] = self._resolve_val(item, components)
                        i += 1
                        arg_idx += 1
                return {
                    "call": head,
                    "args": args_dict,
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
        template_child_id = ""
        items_path = None
        i = 1
        while i < len(expr):
            item = expr[i]
            if isinstance(item, str) and item.startswith(":") and i + 1 < len(expr):
                if item in (":items", ":dataset", ":data", ":source", ":path"):
                    items_path = self._resolve_val(expr[i + 1], components)
                i += 2
            elif isinstance(item, list):
                template_child_id = self._compile_component(item, components)
                i += 1
            else:
                i += 1
        res: Dict[str, Any] = {"componentId": template_child_id}
        if items_path:
            res["items_path"] = items_path
        return res

    def _compile_tabs(self, val: List[Any], components: List[Dict[str, Any]], data_model: Dict[str, Any]) -> List[Dict[str, Any]]:
        tabs_list = []
        for item in val:
            if isinstance(item, list):
                title = ""
                child_id = ""
                i = 0
                while i < len(item):
                    elem = item[i]
                    if isinstance(elem, str) and elem.startswith(":"):
                        k = elem[1:]
                        v = item[i + 1] if i + 1 < len(item) else None
                        if k in ("title", "label") and isinstance(v, str):
                            title = v
                        elif k in ("content", "child", "component") and isinstance(v, list):
                            child_id = self._compile_component(v, components, data_model)
                        i += 2
                    elif isinstance(elem, str):
                        title = elem
                        i += 1
                    elif isinstance(elem, list):
                        child_id = self._compile_component(elem, components, data_model)
                        i += 1
                    else:
                        i += 1
                if title or child_id:
                    tabs_list.append({"title": title, "child": child_id})
        return tabs_list

    def _schema_expects_single_child(self, comp_type: str) -> bool:
        props = self.schema_helper.get_component_properties(comp_type)
        return "child" in props and "children" not in props
