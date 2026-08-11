# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for Phase 2 Python catalog and composition rules."""

import pytest
from a2ui.core.catalog.catalog_definition import (
    CatalogDefinition,
    ComponentDefinition,
    FunctionDefinition,
)
from a2ui.core.catalog.resolver import CatalogResolver
from a2ui.core.validating.composition import (
    ComponentInstance,
    validate_composition,
)


def test_catalog_definition_map_functions():
    catalog_data = {
        "catalogId": "org.example.custom",
        "title": "Custom Catalog",
        "components": {
            "CustomButton": {
                "allowedParents": ["Surface", "Row", "Column"],
            },
        },
        "functions": {
            "calculateTotal": {
                "returnType": "number",
                "callableFrom": "rendererOnly",
            },
        },
    }

    catalog = CatalogDefinition.model_validate(catalog_data)
    assert catalog.catalog_id == "org.example.custom"
    assert catalog.functions["calculateTotal"].return_type == "number"


def test_catalog_definition_rejects_surface_component():
    catalog_data = {
        "catalogId": "invalid",
        "components": {
            "Surface": {},
        },
    }
    with pytest.raises(ValueError, match="cannot be 'Surface'"):
        CatalogDefinition.model_validate(catalog_data)


def test_catalog_definition_rejects_invalid_function_name():
    catalog_data = {
        "catalogId": "invalid",
        "functions": {
            "invalid-fn-name": {
                "returnType": "string",
            },
        },
    }
    with pytest.raises(ValueError, match="must be a valid UAX #31 identifier"):
        CatalogDefinition.model_validate(catalog_data)


def test_catalog_resolver_3_step_fallback():
    default_cat = CatalogDefinition(catalogId="default-cat")
    msg_cat = CatalogDefinition(catalogId="msg-cat")
    surface_cat = CatalogDefinition(catalogId="surface-cat")

    resolver = CatalogResolver(
        catalogs={
            "default-cat": default_cat,
            "msg-cat": msg_cat,
            "surface-cat": surface_cat,
        },
        default_catalog_id="default-cat",
    )

    assert resolver.has_catalog("default-cat") is True
    assert resolver.has_catalog("new-cat") is False

    resolver.register_catalog(CatalogDefinition(catalogId="new-cat"))
    assert resolver.has_catalog("new-cat") is True

    # Step 1: Surface override
    assert resolver.resolve_catalog_id("surface-cat", "msg-cat") == "surface-cat"
    assert resolver.resolve_catalog("surface-cat", "msg-cat") == surface_cat

    # Step 2: Message declared
    assert resolver.resolve_catalog_id(None, "msg-cat") == "msg-cat"
    assert resolver.resolve_catalog(None, "msg-cat") == msg_cat

    # Step 3: Default fallback
    assert resolver.resolve_catalog_id(None, None) == "default-cat"
    assert resolver.resolve_catalog(None, None) == default_cat

    # Unregistered catalog ID returns string ID for resolve_catalog_id, None for resolve_catalog
    assert resolver.resolve_catalog_id("unregistered", None) == "unregistered"
    assert resolver.resolve_catalog("unregistered", None) is None


def test_validate_composition_edge_cases():
    catalog = CatalogDefinition(
        catalogId="test-cat",
        components={
            "Card": ComponentDefinition(
                allowedParents=["Surface", "Column"],
                allowedChildren=["Text", "Button"],
            ),
            "Text": ComponentDefinition(allowedParents=["Card", "Column"]),
            "Button": ComponentDefinition(allowedParents=["Card"]),
            "Orphan": ComponentDefinition(allowedParents=[]),
            "LeafContainer": ComponentDefinition(allowedChildren=[]),
        },
    )

    # Empty allowedParents disallows any parent
    comps = [
        ComponentInstance(id="root", type="Surface", children=["orphan1"]),
        ComponentInstance(id="orphan1", type="Orphan", parentId="root"),
    ]
    errors = validate_composition(comps, "root", catalog)
    assert len(errors) == 1
    assert errors[0].rule == "allowed_parents"

    # Empty allowedChildren disallows any child
    comps = [
        ComponentInstance(id="root", type="Surface", children=["leaf1"]),
        ComponentInstance(
            id="leaf1", type="LeafContainer", parentId="root", children=["text1"]
        ),
        ComponentInstance(id="text1", type="Text", parentId="leaf1"),
    ]
    errors = validate_composition(comps, "root", catalog)
    assert (
        len(errors) == 2
    )  # Triggers allowed_children on leaf1 AND allowed_parents on text1

    # Dangling parent reference
    comps = [
        ComponentInstance(id="root", type="Surface"),
        ComponentInstance(id="text1", type="Text", parentId="non_existent"),
    ]
    errors = validate_composition(comps, "root", catalog)
    assert len(errors) == 1
    assert errors[0].rule == "allowed_parents"

    # Dangling child reference
    comps = [
        ComponentInstance(id="root", type="Surface", children=["card1"]),
        ComponentInstance(
            id="card1", type="Card", parentId="root", children=["non_existent"]
        ),
    ]
    errors = validate_composition(comps, "root", catalog)
    assert len(errors) == 1
    assert errors[0].rule == "allowed_children"
