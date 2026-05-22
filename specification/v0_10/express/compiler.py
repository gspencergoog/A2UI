"""Compilation engine for A2UI Express.

Tokenizes, lexes, and parses A2UI Express plain-text statements into a clean
AST, compiling it directly into standard A2UI v0.10 JSON messages.
"""

import re
from typing import Any, Optional
from .schema_helper import CatalogSchemaHelper

# Scanner rules for lexical tokenizing
TOKEN_SPEC = [
    ('STRING', r'"(?:[^"\\]|\\.)*"'),
    ('PATH', r'\$[a-zA-Z0-9_/]+'),
    ('CHECK', r'\?[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUMBER', r'-?\d+(?:\.\d+)?'),
    ('BOOLEAN', r'\b(?:true|false)\b'),
    ('NULL', r'\bnull\b'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_-]*'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('COMMA', r','),
    ('EQUALS', r'='),
    ('COLON', r':'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('WS', r'\s+'),
]


def tokenize(text: str) -> list[tuple[str, Any]]:
    """Tokenizes plain text into a list of scanning tokens.

    Args:
        text: The source line to tokenize.

    Returns:
        A list of token tuples matching (TokenKind, TokenValue).
    """
    tok_regex = '|'.join(f'(?P<{name}>{pattern})'
                         for name, pattern in TOKEN_SPEC)
    tokens = []
    for mo in re.finditer(tok_regex, text):
        kind = mo.lastgroup
        val = mo.group()
        if kind == 'WS':
            continue
        elif kind == 'STRING':
            val = val[1:-1].replace('\\"', '"')
        elif kind == 'NUMBER':
            val = float(val) if '.' in val else int(val)
        elif kind == 'BOOLEAN':
            val = val == 'true'
        elif kind == 'NULL':
            val = None
        tokens.append((kind, val))
    return tokens


class TokenParser:
    """Recursive-descent parser for A2UI Express expressions.

    Parses tokenized structures (calls, arrays, maps, data paths, primitives)
    into intermediate syntax trees.
    """

    def __init__(self, tokens: list[tuple[str, Any]]):
        """Initializes the parser with the scanner token list.

        Args:
            tokens: The scanner token list.
        """
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[tuple[str, Any]]:
        """Returns the current token without consuming it.

        Returns:
            The current token tuple, or None if at EOF.
        """
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, kind: Optional[str] = None) -> tuple[str, Any]:
        """Consumes the current token, asserting its type if requested.

        Args:
            kind: Optional token kind to assert.

        Returns:
            The consumed token tuple.

        Raises:
            SyntaxError: If the token is missing or does not match kind.
        """
        tok = self.peek()
        if not tok:
            raise SyntaxError("Unexpected end of input")
        if kind and tok[0] != kind:
            raise SyntaxError(f"Expected {kind}, got {tok[0]}: {tok[1]}")
        self.pos += 1
        return tok

    def parse_expression(self) -> Any:
        """Parses a standalone expression.

        Returns:
            The parsed expression AST node.

        Raises:
            SyntaxError: If the expression structure is invalid.
        """
        tok = self.peek()
        if not tok:
            raise SyntaxError("Expected expression")

        kind, val = tok
        if kind == 'LBRACKET':
            return self.parse_array()
        if kind == 'PATH':
            self.consume()
            return {"path": val[1:]}
        if kind == 'CHECK':
            return self.parse_check()
        if kind == 'IDENTIFIER':
            self.consume()
            next_tok = self.peek()
            if next_tok and next_tok[0] == 'LPAREN':
                return self.parse_call(val)
            return {"variable": val}
        if kind in ('STRING', 'NUMBER', 'BOOLEAN', 'NULL'):
            self.consume()
            return val
        raise SyntaxError(f"Unexpected token {kind}: {val}")

    def parse_array(self) -> list:
        """Parses an array of expressions.

        Returns:
            A list of parsed expression AST nodes.
        """
        self.consume('LBRACKET')
        items = []
        if self.peek() and self.peek()[0] != 'RBRACKET':
            items.append(self.parse_expression())
            while self.peek() and self.peek()[0] == 'COMMA':
                self.consume('COMMA')
                items.append(self.parse_expression())
        self.consume('RBRACKET')
        return items

    def parse_check(self) -> dict:
        """Parses a check validation expression.

        Returns:
            A check rule AST dictionary.
        """
        tok = self.consume('CHECK')
        name = tok[1][1:]  # strip ?
        next_tok = self.peek()
        args = []
        if next_tok and next_tok[0] == 'LPAREN':
            self.consume('LPAREN')
            if self.peek() and self.peek()[0] != 'RPAREN':
                args.append(self.parse_expression())
                while self.peek() and self.peek()[0] == 'COMMA':
                    self.consume('COMMA')
                    args.append(self.parse_expression())
            self.consume('RPAREN')
        return {"check": name, "args": args}

    def parse_call(self, name: str) -> dict:
        """Parses a component or function call.

        Args:
            name: The identifier name of the component or function.

        Returns:
            A call AST dictionary.
        """
        self.consume('LPAREN')
        args = []
        if self.peek() and self.peek()[0] != 'RPAREN':
            if self.peek()[0] == 'LBRACE':
                args.append(self.parse_map())
            else:
                args.append(self.parse_expression())

            while self.peek() and self.peek()[0] == 'COMMA':
                self.consume('COMMA')
                if self.peek()[0] == 'LBRACE':
                    args.append(self.parse_map())
                else:
                    args.append(self.parse_expression())
        self.consume('RPAREN')
        return {"call": name, "args": args}

    def parse_map(self) -> dict:
        """Parses a key-value dictionary block.

        Returns:
            A dictionary mapping string keys to parsed expressions.
        """
        self.consume('LBRACE')
        res = {}
        if self.peek() and self.peek()[0] != 'RBRACE':
            k_tok = self.consume('IDENTIFIER')
            self.consume('COLON')
            v = self.parse_expression()
            res[k_tok[1]] = v
            while self.peek() and self.peek()[0] == 'COMMA':
                self.consume('COMMA')
                k_tok = self.consume('IDENTIFIER')
                self.consume('COLON')
                v = self.parse_expression()
                res[k_tok[1]] = v
        self.consume('RBRACE')
        return res


class ExpressCompiler:
    """Compilation pipeline for A2UI Express.

    Resolves positional parameters dynamically, flattens variable references into
    an adjacency list widget tree, and constructs valid A2UI v0.10 JSON payloads.

    Attributes:
        helper: A CatalogSchemaHelper loaded with the target catalog definition.
    """

    def __init__(self, catalog_path: str):
        """Initializes the compiler with the specified catalog schema.

        Args:
            catalog_path: The absolute filesystem path to the catalog JSON file.
        """
        self.helper = CatalogSchemaHelper(catalog_path)

    def compile(self,
                dsl_text: str,
                surface_id: str = "default_surface",
                catalog_id: str = "") -> dict:
        """Compiles plain A2UI Express DSL into standard A2UI v0.10 wire JSON.

        Args:
            dsl_text: The source A2UI Express DSL text block.
            surface_id: The unique identifier for the compiled user interface surface.
            catalog_id: The URI/identifier of the schema catalog to reference.

        Returns:
            The standard A2UI v0.10 JSON envelope.

        Raises:
            ValueError: If the root component variable is missing.
        """
        lines = [
            line.strip() for line in dsl_text.splitlines() if line.strip()
        ]
        raw_symbols = {}

        # Line parser and error recovery loop
        for line in lines:
            if "=" not in line:
                continue
            var_part, expr_part = line.split("=", 1)
            var_name = var_part.strip()
            expr_text = expr_part.strip()

            try:
                tokens = tokenize(expr_text)
                parser = TokenParser(tokens)
                raw_symbols[var_name] = parser.parse_expression()
            except Exception:
                # Recover gracefully: register dummy loading text for the failed branch
                raw_symbols[var_name] = {
                    "call": "Text",
                    "args": ["Loading..."]
                }

        compiled_components = []

        # Adjacency list flattening starting at root
        if "root" not in raw_symbols:
            raise ValueError(
                "A2UI Express source must define a 'root' variable.")

        for var_name, ast in raw_symbols.items():
            comp_dict = self._compile_ast_node(var_name, ast, raw_symbols)
            if comp_dict:
                compiled_components.append(comp_dict)

        # Resolve catalog ID
        if not catalog_id:
            catalog_id = self.helper.catalog.get(
                "catalogId", "https://a2ui.org/catalog.json")

        envelope = {
            "version": "v0.10",
            "createSurface": {
                "surfaceId": surface_id,
                "catalogId": catalog_id,
                "components": compiled_components
            }
        }
        return envelope

    def _compile_ast_node(self, var_name: str, ast: Any,
                          raw_symbols: dict) -> Optional[dict]:
        """Compiles a single variable's AST node into standard component format.

        Args:
            var_name: The variable identifier (which becomes the component ID).
            ast: The parsed expression AST node.
            raw_symbols: A dictionary containing all other parsed variables.

        Returns:
            The compiled component JSON dictionary, or None if it is not a component.
        """
        if not isinstance(ast, dict) or "call" not in ast:
            return None

        comp_name = ast["call"]
        args = ast["args"]

        if comp_name not in self.helper.components:
            # Not a component, could be a standalone action/helper; skip writing as component
            return None

        properties = self.helper.get_component_properties(comp_name)
        comp_dict = {"id": var_name, "component": comp_name}

        # Sibling path tracking for check rules
        sibling_value_path = None

        # First pass: map basic properties
        for idx, arg in enumerate(args):
            if idx >= len(properties):
                break
            prop_name = properties[idx]
            if prop_name == "checks":
                continue  # Compile checks in second pass

            mapped_val = self._compile_value(
                arg,
                raw_symbols,
                is_action=(prop_name in ["action", "submitAction"]))
            comp_dict[prop_name] = mapped_val

            if prop_name == "value" and isinstance(
                    mapped_val, dict) and "path" in mapped_val:
                sibling_value_path = mapped_val

        # Second pass: compile checks with implicit path injection
        for idx, arg in enumerate(args):
            if idx >= len(properties):
                break
            prop_name = properties[idx]
            if prop_name == "checks":
                compiled_checks = []
                raw_checks = arg if isinstance(arg, list) else [arg]
                for rc in raw_checks:
                    if isinstance(rc, dict) and "check" in rc:
                        check_name = rc["check"]
                        check_args = rc["args"]
                        compiled_args = {}

                        check_props = self.helper.get_function_properties(
                            check_name)
                        message_val = f"{check_name.capitalize()} check failed"

                        explicit_args = list(check_args)
                        is_value_injected = False

                        # Handle implicit target 'value' injection
                        if check_props and check_props[0] == "value":
                            if explicit_args and isinstance(
                                    explicit_args[0],
                                    dict) and "path" in explicit_args[0]:
                                pass
                            else:
                                if sibling_value_path:
                                    compiled_args["value"] = sibling_value_path
                                    is_value_injected = True

                        start_prop_idx = 1 if is_value_injected else 0

                        for c_idx, c_arg in enumerate(explicit_args):
                            prop_target_idx = c_idx + start_prop_idx
                            if prop_target_idx < len(check_props):
                                compiled_args[check_props[
                                    prop_target_idx]] = self._compile_value(
                                        c_arg, raw_symbols)
                            else:
                                if isinstance(c_arg, str):
                                    message_val = c_arg

                        compiled_checks.append({
                            "condition": {
                                "call": check_name,
                                "args": compiled_args
                            },
                            "message": message_val
                        })
                comp_dict["checks"] = compiled_checks

        return comp_dict

    def _compile_value(self,
                       val: Any,
                       raw_symbols: dict,
                       is_action: bool = False) -> Any:
        """Compiles an individual AST node value into valid A2UI equivalents.

        Args:
            val: The parsed AST node value.
            raw_symbols: The parsed global variable symbol table.
            is_action: Whether this value lies inside a component Action field.

        Returns:
            The semantically correct A2UI JSON structure.
        """
        if isinstance(val, dict):
            if "path" in val:
                return val
            if "variable" in val:
                # Resolve variable ID
                return val["variable"]
            if "call" in val:
                # Nested function call (e.g. formatString or actions)
                fn_name = val["call"]
                fn_args = val["args"]

                # Is it a reserved Template signature?
                if fn_name == "Template":
                    path_val = self._compile_value(fn_args[0], raw_symbols,
                                                   is_action)
                    comp_id_val = self._compile_value(fn_args[1], raw_symbols,
                                                      is_action)
                    return {
                        "path": path_val["path"],
                        "componentId": comp_id_val
                    }

                # Is it a reserved Event signature?
                if fn_name == "Event":
                    event_name = fn_args[0] if len(fn_args) > 0 else ""
                    context_map = fn_args[1] if len(fn_args) > 1 else {}
                    compiled_context = {}
                    for k, v in context_map.items():
                        compiled_context[k] = self._compile_value(
                            v, raw_symbols, is_action)
                    return {
                        "event": {
                            "name": event_name,
                            "context": compiled_context
                        }
                    }

                # Is it a regular catalog function?
                if fn_name in self.helper.functions:
                    fn_props = self.helper.get_function_properties(fn_name)
                    compiled_args = {}
                    for idx, arg in enumerate(fn_args):
                        if idx < len(fn_props):
                            compiled_args[fn_props[idx]] = self._compile_value(
                                arg, raw_symbols, is_action)

                    # Wrap in functionCall only if inside an action field
                    if is_action:
                        return {
                            "functionCall": {
                                "call": fn_name,
                                "args": compiled_args
                            }
                        }

                    # Otherwise, compile direct dynamic function call expression (with returnType!)
                    res_expr = {"call": fn_name, "args": compiled_args}
                    # Read returnType from catalog definition if present
                    fn_def = self.helper.functions.get(fn_name, {})
                    return_type_const = fn_def.get("properties",
                                                   {}).get("returnType",
                                                           {}).get("const")
                    if return_type_const:
                        res_expr["returnType"] = return_type_const
                    return res_expr

                # Fallback
                return {
                    "call":
                    fn_name,
                    "args": [
                        self._compile_value(a, raw_symbols, is_action)
                        for a in fn_args
                    ]
                }

            return {
                k: self._compile_value(v, raw_symbols, is_action)
                for k, v in val.items()
            }

        if isinstance(val, list):
            # If this is a list of elements, compile each element
            compiled_list = []
            for item in val:
                comp_item = self._compile_value(item, raw_symbols, is_action)
                compiled_list.append(comp_item)
            return compiled_list

        return val
