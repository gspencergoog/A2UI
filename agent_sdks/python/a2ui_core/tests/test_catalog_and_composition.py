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

    # Step 1: Surface override
    assert resolver.resolve_catalog_id("surface-cat", "msg-cat") == "surface-cat"
    # Step 2: Message declared
    assert resolver.resolve_catalog_id(None, "msg-cat") == "msg-cat"
    # Step 3: Default fallback
    assert resolver.resolve_catalog_id(None, None) == "default-cat"


def test_validate_composition_root_surface():
    invalid_comps = [ComponentInstance(id="root", type="Column")]
    errors = validate_composition(invalid_comps, "root")
    assert len(errors) == 1
    assert errors[0].rule == "surface_root"

    valid_comps = [ComponentInstance(id="root", type="Surface")]
    errors = validate_composition(valid_comps, "root")
    assert len(errors) == 0


def test_validate_composition_parent_child_rules():
    catalog = CatalogDefinition(
        catalogId="test-cat",
        components={
            "Card": ComponentDefinition(
                allowedParents=["Surface", "Column"],
                allowedChildren=["Text", "Button"],
            ),
            "Text": ComponentDefinition(allowedParents=["Card", "Column"]),
            "Button": ComponentDefinition(allowedParents=["Card"]),
        },
    )

    # Invalid Parent: Button under Surface root directly (Button requires Card parent)
    comps = [
        ComponentInstance(id="root", type="Surface", children=["btn1"]),
        ComponentInstance(id="btn1", type="Button", parentId="root"),
    ]
    errors = validate_composition(comps, "root", catalog)
    assert len(errors) == 1
    assert errors[0].rule == "allowed_parents"

    # Invalid Child: Image inside Card (Card allows Text, Button only)
    comps = [
        ComponentInstance(id="root", type="Surface", children=["card1"]),
        ComponentInstance(id="card1", type="Card", parentId="root", children=["img1"]),
        ComponentInstance(id="img1", type="Image", parentId="card1"),
    ]
    errors = validate_composition(comps, "root", catalog)
    assert len(errors) == 1
    assert errors[0].rule == "allowed_children"
