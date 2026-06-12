"""Compiles A2UI Express DSL (S-expressions) into createSurface JSON envelopes."""

import re
from typing import Any, Optional

try:
    # pylint: disable=relative-beyond-top-level
    from .schema_helper import CatalogSchemaHelper
except (ImportError, ValueError):
    from schema_helper import CatalogSchemaHelper


def _set_nested_path(d: dict, path_str: str, val: Any) -> None:
    if path_str.startswith("@/"):
        clean_path = path_str[2:]
    elif path_str.startswith("@"):
        clean_path = path_str[1:]
    elif path_str.startswith("/"):
        clean_path = path_str[1:]
    else:
        clean_path = path_str
    if not clean_path:
        return
    keys = clean_path.split("/")
    current = d
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = val


TOKEN_SPEC = [
    ('STRING', r'"(?:[^"\\]|\\.)*"'),
    ('PATH', r'@[a-zA-Z0-9_/]+'),
    ('CHECK', r'\?[a-zA-Z_][a-zA-Z0-9_]*'),
    ('EVENT', r'![a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUMBER', r'-?\d+(?:\.\d+)?'),
    ('BOOLEAN', r'\b(?:true|false)\b'),
    ('NULL', r'~'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_-]*'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('EQUALS', r'='),
    ('WS', r'\s+'),
]


def tokenize(text: str) -> list[tuple[str, Any]]:
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
    tokens = []
    for mo in re.finditer(tok_regex, text):
        kind = mo.lastgroup
        val = mo.group()
        if kind == 'WS': continue
        elif kind == 'STRING': val = val[1:-1].replace('\\"', '"')
        elif kind == 'NUMBER': val = float(val) if '.' in val else int(val)
        elif kind == 'BOOLEAN': val = val == 'true'
        elif kind == 'NULL': val = None
        tokens.append((kind, val))
    return tokens


class TokenParser:
    def __init__(self, tokens: list[tuple[str, Any]]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[tuple[str, Any]]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, kind: Optional[str] = None) -> tuple[str, Any]:
        tok = self.peek()
        if not tok: raise SyntaxError("Unexpected end of input")
        if kind and tok[0] != kind: raise SyntaxError(f"Expected {kind}, got {tok[0]}: {tok[1]}")
        self.pos += 1
        return tok

    def parse_expression(self) -> Any:
        tok = self.peek()
        if not tok: raise SyntaxError("Expected expression")
        kind, val = tok
        if kind == 'LPAREN': return self.parse_list_or_call()
        if kind == 'LBRACKET': return self.parse_array()
        if kind == 'LBRACE': return self.parse_map()
        if kind == 'PATH':
            self.consume()
            return {"path": val[1:]}
        if kind == 'CHECK':
            self.consume()
            return {"check": val[1:], "args": []}
        if kind == 'IDENTIFIER':
            self.consume()
            return val
        if kind in ('STRING', 'NUMBER', 'BOOLEAN', 'NULL'):
            self.consume()
            return val
        raise SyntaxError(f"Unexpected token {kind}: {val}")

    def parse_list_or_call(self) -> Any:
        self.consume('LPAREN')
        first_tok = self.peek()
        if not first_tok: raise SyntaxError("Unexpected EOF in list")
        if first_tok[0] == 'EQUALS':
            self.consume('EQUALS')
            path_expr = self.parse_expression()
            val_expr = self.parse_expression()
            self.consume('RPAREN')
            return {"assignment": path_expr, "value": val_expr}
        if first_tok[0] == 'CHECK':
            check_tok = self.consume('CHECK')
            args = []
            while self.peek() and self.peek()[0] != 'RPAREN':
                args.append(self.parse_expression())
            self.consume('RPAREN')
            return {"check": check_tok[1][1:], "args": args}
        if first_tok[0] == 'EVENT':
            evt_tok = self.consume('EVENT')
            args = []
            while self.peek() and self.peek()[0] != 'RPAREN':
                args.append(self.parse_expression())
            self.consume('RPAREN')
            return {"call": "Event", "args": [evt_tok[1][1:]] + args}
        if first_tok[0] == 'IDENTIFIER':
            name_tok = self.consume('IDENTIFIER')
            args = []
            while self.peek() and self.peek()[0] != 'RPAREN':
                args.append(self.parse_expression())
            self.consume('RPAREN')
            return {"call": name_tok[1], "args": args}
        raise SyntaxError(f"Invalid list start: {first_tok}")

    def parse_array(self) -> list:
        self.consume('LBRACKET')
        items = []
        while self.peek() and self.peek()[0] != 'RBRACKET':
            items.append(self.parse_expression())
        self.consume('RBRACKET')
        return items

    def parse_map(self) -> dict:
        self.consume('LBRACE')
        res = {}
        while self.peek() and self.peek()[0] != 'RBRACE':
            k_tok = self.consume('IDENTIFIER')
            v = self.parse_expression()
            res[k_tok[1]] = v
        self.consume('RBRACE')
        return res


class ExpressCompiler:
    def __init__(self, catalog_path: str):
        self.helper = CatalogSchemaHelper(catalog_path)
        self.compiled_components = []
        self.id_counter = 0

    def compile(self, dsl_text: str, surface_id: str = "default_surface", catalog_id: str = "") -> dict:
        if "<a2ui>" in dsl_text:
            dsl_text = dsl_text.split("<a2ui>")[1].split("</a2ui>")[0]
            
        tokens = tokenize(dsl_text)
        parser = TokenParser(tokens)
        
        expressions = []
        while parser.peek():
            expressions.append(parser.parse_expression())
            
        data_model = {}
        root_ast = None
        
        for expr in expressions:
            if isinstance(expr, dict) and "assignment" in expr:
                path_dict = expr["assignment"]
                if isinstance(path_dict, dict) and "path" in path_dict:
                    compiled_val = self._compile_value(expr["value"], {})
                    _set_nested_path(data_model, path_dict["path"], compiled_val)
            elif root_ast is None:
                root_ast = expr
                
        if not root_ast:
            raise ValueError("A2UI Express source must define a root component.")
            
        self.compiled_components = []
        self.id_counter = 0
        
        self._compile_ast_node(root_ast, is_root=True)
        
        if not catalog_id:
            catalog_id = self.helper.catalog.get("catalogId", "https://a2ui.org/catalog.json")
            
        envelope = {
            "version": "v1.0",
            "createSurface": {
                "surfaceId": surface_id,
                "catalogId": catalog_id,
                "components": self.compiled_components
            }
        }
        
        if data_model:
            envelope["createSurface"]["dataModel"] = data_model
            
        return envelope

    def _compile_ast_node(self, ast: Any, is_root: bool = False) -> str:
        comp_name = ast["call"]
        args = ast["args"]
        
        comp_id = "root" if is_root else f"{comp_name.lower()}_{self.id_counter}"
        if not is_root:
            self.id_counter += 1
            
        properties = self.helper.get_component_properties(comp_name)
        comp_dict = {"id": comp_id, "component": comp_name}
        
        for p in properties:
            if p != "checks":
                comp_dict[p] = None
                
        sibling_value_path = None
        for idx, arg in enumerate(args):
            if idx >= len(properties): break
            prop_name = properties[idx]
            if prop_name == "checks": continue
            
            mapped_val = self._compile_value(arg, {}, is_action=(prop_name in ["action", "submitAction"]))
            comp_dict[prop_name] = mapped_val
            
            if prop_name == "value" and isinstance(mapped_val, dict) and "path" in mapped_val:
                sibling_value_path = mapped_val
                
        for idx, arg in enumerate(args):
            if idx >= len(properties): break
            prop_name = properties[idx]
            if prop_name == "checks":
                compiled_checks = []
                raw_checks = arg if isinstance(arg, list) else [arg]
                for rc in raw_checks:
                    if isinstance(rc, dict) and "check" in rc:
                        check_name = rc["check"]
                        check_args = rc["args"]
                        compiled_args = {}
                        check_props = self.helper.get_function_properties(check_name)
                        message_val = f"{check_name.capitalize()} check failed"
                        
                        is_value_injected = False
                        if check_props and check_props[0] == "value" and sibling_value_path:
                            if not (check_args and isinstance(check_args[0], dict) and "path" in check_args[0]):
                                compiled_args["value"] = sibling_value_path
                                is_value_injected = True
                                
                        start_prop_idx = 1 if is_value_injected else 0
                        for c_idx, c_arg in enumerate(check_args):
                            prop_target_idx = c_idx + start_prop_idx
                            if prop_target_idx < len(check_props):
                                compiled_args[check_props[prop_target_idx]] = self._compile_value(c_arg, {})
                            else:
                                if isinstance(c_arg, str):
                                    message_val = c_arg
                                    
                        compiled_checks.append({
                            "condition": {"call": check_name, "args": compiled_args},
                            "message": message_val
                        })
                comp_dict["checks"] = compiled_checks
                
        self.compiled_components.append(comp_dict)
        return comp_id

    def _compile_value(self, val: Any, raw_symbols: dict, is_action: bool = False) -> Any:
        if isinstance(val, dict):
            if "path" in val: return val
            if "call" in val:
                fn_name = val["call"]
                fn_args = val["args"]
                
                if fn_name in self.helper.components:
                    return self._compile_ast_node(val)
                    
                if fn_name == "Template":
                    path_val = self._compile_value(fn_args[0], raw_symbols, is_action)
                    comp_id_val = self._compile_value(fn_args[1], raw_symbols, is_action)
                    return {"path": path_val["path"], "componentId": comp_id_val}
                    
                if fn_name == "Event":
                    event_name = fn_args[0] if len(fn_args) > 0 else ""
                    context_map = fn_args[1] if len(fn_args) > 1 else {}
                    compiled_context = {k: self._compile_value(v, raw_symbols, is_action) for k, v in context_map.items()}
                    return {"event": {"name": event_name, "context": compiled_context}}
                    
                if fn_name in self.helper.functions:
                    fn_props = self.helper.get_function_properties(fn_name)
                    compiled_args = {}
                    for idx, arg in enumerate(fn_args):
                        if idx < len(fn_props):
                            compiled_args[fn_props[idx]] = self._compile_value(arg, raw_symbols, is_action)
                    if is_action:
                        return {"functionCall": {"call": fn_name, "args": compiled_args}}
                        
                    res_expr = {"call": fn_name, "args": compiled_args}
                    fn_def = self.helper.functions.get(fn_name, {})
                    return_type_const = fn_def.get("returnType") or fn_def.get("properties", {}).get("returnType", {}).get("const")
                    if return_type_const:
                        res_expr["returnType"] = return_type_const
                    return res_expr
                    
                return {"call": fn_name, "args": [self._compile_value(a, raw_symbols, is_action) for a in fn_args]}
                
            return {k: self._compile_value(v, raw_symbols, is_action) for k, v in val.items()}
            
        if isinstance(val, list):
            return [self._compile_value(item, raw_symbols, is_action) for item in val]
            
        return val