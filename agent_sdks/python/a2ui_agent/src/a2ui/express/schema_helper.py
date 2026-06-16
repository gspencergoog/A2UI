"""Utility for parsing A2UI component and function catalogs.

Provides dynamic schema crawling to identify component properties, logical function
signatures, and requirements directly from standard catalog JSON schemas.
"""

import json


class CatalogSchemaHelper:
    """Dynamic schema crawler for A2UI catalogs.

    Resolves component and function properties in strict schema definition order
    to support positional parameter mapping for compact generative notations.

    Attributes:
        catalog_path: The absolute filesystem path to the catalog JSON file.
        catalog: The parsed catalog JSON dictionary.
        components: A dictionary mapping component names to their catalog schemas.
        functions: A dictionary mapping function names to their catalog schemas.
    """

    def __init__(self, catalog_path: str):
        """Initializes the helper by loading and parsing the catalog file.

        Args:
            catalog_path: The absolute filesystem path to the catalog JSON file.
        """
        self.catalog_path = catalog_path
        with open(catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)
        self.components = self.catalog.get("components", {})
        self.functions = self.catalog.get("functions", {})
        self._load_mappings()

    def _load_mappings(self):
        """Crawls the component and function schemas to build internal mappings."""
        self.component_properties = {}
        self.component_required = {}
        self.component_is_checkable = {}

        for name, schema in self.components.items():
            props = {}
            reqs = []
            is_checkable = False

            # Crawl allOf and root schema for properties
            sub_schemas = [schema]
            if "allOf" in schema:
                sub_schemas.extend(schema["allOf"])

            for sub in sub_schemas:
                if "$ref" in sub:
                    ref = sub["$ref"]
                    if "Checkable" in ref:
                        is_checkable = True
                if "properties" in sub:
                    props.update(sub["properties"])
                if "required" in sub:
                    reqs.extend(sub["required"])

            # Filter out structural properties component and id
            ordered_keys = []
            for k in props:
                if k not in ["component", "id"]:
                    ordered_keys.append(k)

            # If it's checkable, add checks at the end
            if is_checkable:
                ordered_keys.append("checks")

            self.component_properties[name] = ordered_keys
            self.component_required[name] = reqs
            self.component_is_checkable[name] = is_checkable

        self.function_properties = {}
        self.function_required = {}

        for name, schema in self.functions.items():
            args_obj = schema.get("properties", {}).get("args", {})
            props = args_obj.get("properties", {})
            reqs = args_obj.get("required", [])
            self.function_properties[name] = list(props.keys())
            self.function_required[name] = reqs

    def get_component_properties(self, name: str) -> list[str]:
        """Returns the ordered properties of the specified component.

        Args:
            name: The catalog name of the component.

        Returns:
            A list of property keys in their schema definition order.
        """
        return self.component_properties.get(name, [])

    def get_component_required(self, name: str) -> list[str]:
        """Returns the list of required properties for the specified component.

        Args:
            name: The catalog name of the component.

        Returns:
            A list of property keys that are required.
        """
        return self.component_required.get(name, [])

    def is_checkable(self, name: str) -> bool:
        """Returns whether the specified component supports client-side checks.

        Args:
            name: The catalog name of the component.

        Returns:
            Whether the component implements the Checkable interface.
        """
        return self.component_is_checkable.get(name, False)

    def get_function_properties(self, name: str) -> list[str]:
        """Returns the ordered properties of the specified function's arguments.

        Args:
            name: The catalog name of the function.

        Returns:
            A list of function parameter names in their schema definition order.
        """
        return self.function_properties.get(name, [])

    def get_function_required(self, name: str) -> list[str]:
        """Returns the list of required argument properties for the function.

        Args:
            name: The catalog name of the function.

        Returns:
            A list of function parameter names that are required.
        """
        return self.function_required.get(name, [])
