"""Prompt compiler for A2UI Express.

Compiles standard JSON catalog schemas into compact plain-text signatures and
instruction blocks for on-device models (e.g., Gemma 4).
"""

from .schema_helper import CatalogSchemaHelper


class ExpressPromptGenerator:
    """Generates system prompt contracts guiding models to produce A2UI Express.

    Compiles component catalog structures and logic helper catalogs into standard
    positional signatures, reducing prompt token utilization.

    Attributes:
        helper: A CatalogSchemaHelper instance loaded with the target catalog.
    """

    def __init__(self, catalog_path: str):
        """Initializes the generator with the specified catalog path.

        Args:
            catalog_path: The absolute filesystem path to the catalog JSON file.
        """
        self.helper = CatalogSchemaHelper(catalog_path)

    def generate_component_signatures(self) -> str:
        """Compiles component definitions into clean function-like signatures.

        Returns:
            A plain-text multi-line list of component signatures.
        """
        signatures = []
        for name in sorted(self.helper.component_properties.keys()):
            props = self.helper.get_component_properties(name)
            reqs = self.helper.get_component_required(name)
            ordered_args = []
            for p in props:
                is_req = p in reqs
                opt_suffix = "" if is_req else "?"
                ordered_args.append(f"{p}{opt_suffix}")
            sig = f"• {name}({', '.join(ordered_args)})"
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
            ordered_args = []
            for p in props:
                is_req = p in reqs
                opt_suffix = "" if is_req else "?"
                ordered_args.append(f"{p}{opt_suffix}")
            sig = f"• {name}({', '.join(ordered_args)})"
            signatures.append(sig)
        return "\n".join(signatures)

    def generate_prompt(self) -> str:
        """Assembles the complete system instruction block for the LLM.

        Returns:
            The full system prompt string explaining A2UI Express and its catalog.
        """
        comp_sigs = self.generate_component_signatures()
        func_sigs = self.generate_function_signatures()

        prompt = f"""# A2UI Express Output Contract

You must output the user interface using the compact A2UI Express DSL notation.

## Grammar Rules

1. Output exactly one variable assignment statement per line:
   variable_name = ComponentName(arg1, arg2, ...)

2. The interface tree must have a single entry point assigned to the reserved variable 'root'.

3. Primitives:
   - Strings: enclose in double quotes, e.g., "label"
   - Numbers: write as integers or decimals, e.g., 42
   - Booleans: write true or false
   - Null values: write null

4. Lists: represent as arrays, e.g., [child1, child2]

5. Data bindings: prefix absolute paths in the data model with '$', e.g., $/user/firstName.
   Prefix relative list scopes with '$', e.g., $firstName.

6. Logic and validation: prefix client check rules with '?', e.g., ?required or
   ?regex("^[0-9]{5}$").

7. Action events: represent server-side actions using the Event helper:
   Event("save_deal", {{rep: $/form/rep}})

8. Nested functions: call client functions directly using catalog signatures,
   for example openUrl("https://example.com").

## Positional Component Signatures

Use these exact positional signatures to instantiate components. Do not output property keys:
{comp_sigs}

## Positional Function Signatures

Use these exact positional signatures to instantiate check rules or logic functions:
{func_sigs}

## Examples

```
root = Column([repField, valueField])
repField = TextField("Representative", $/form/rep, "Enter name")
valueField = TextField("Deal Value", $/form/value, "0.00", "number", [?required])
```
"""
        return prompt
