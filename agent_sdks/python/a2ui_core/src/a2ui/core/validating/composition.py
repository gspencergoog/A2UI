"""Component Composition Rules and Validation for A2UI v1.0 in Python.

Enforces surface root component rules ("Surface" as root) and container
parent/child component relationship constraints.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from a2ui.core.catalog.catalog_definition import CatalogDefinition, ComponentDefinition


class ComponentInstance(BaseModel):
    """Simple model representing a component instance in a surface."""

    id: str
    type: str
    parent_id: Optional[str] = Field(default=None, alias="parentId")
    children: Optional[List[str]] = Field(default=None)


class CompositionValidationError(BaseModel):
    """Details of a composition validation error."""

    component_id: str
    message: str
    rule: str  # 'surface_root' | 'allowed_parents' | 'allowed_children'


def validate_composition(
    components: List[ComponentInstance],
    root_component_id: str,
    catalog: Optional[CatalogDefinition] = None,
) -> List[CompositionValidationError]:
    """Validates surface composition rules across components in a surface."""
    errors: List[CompositionValidationError] = []
    comp_map: Dict[str, ComponentInstance] = {c.id: c for c in components}

    # 1. Surface Root Component Rule
    root_comp = comp_map.get(root_component_id)
    if not root_comp:
        errors.append(
            CompositionValidationError(
                component_id=root_component_id,
                message=f"Root component '{root_component_id}' not found in surface.",
                rule="surface_root",
            )
        )
    elif root_comp.type != "Surface":
        errors.append(
            CompositionValidationError(
                component_id=root_component_id,
                message=f"Surface root component must be of type 'Surface', got '{root_comp.type}'.",
                rule="surface_root",
            )
        )

    # 2. Parent / Child Constraints (if catalog provided)
    if catalog and catalog.components:
        catalog_comps = catalog.components

        for comp in components:
            def_item: Optional[ComponentDefinition] = catalog_comps.get(comp.type)
            if not def_item:
                continue

            # Allowed Parents Validation
            if comp.parent_id:
                parent_comp = comp_map.get(comp.parent_id)
                if not parent_comp:
                    errors.append(
                        CompositionValidationError(
                            component_id=comp.id,
                            message=f"Component '{comp.id}' references parent '{comp.parent_id}' which does not exist.",
                            rule="allowed_parents",
                        )
                    )
                elif def_item.allowed_parents is not None:
                    if parent_comp.type not in def_item.allowed_parents:
                        errors.append(
                            CompositionValidationError(
                                component_id=comp.id,
                                message=(
                                    f"Component '{comp.id}' of type '{comp.type}' is not allowed under "
                                    f"parent '{parent_comp.id}' of type '{parent_comp.type}'."
                                ),
                                rule="allowed_parents",
                            )
                        )

            # Allowed Children Validation
            if comp.children and def_item.allowed_children is not None:
                for child_id in comp.children:
                    child_comp = comp_map.get(child_id)
                    if not child_comp:
                        errors.append(
                            CompositionValidationError(
                                component_id=comp.id,
                                message=f"Container '{comp.id}' references child '{child_id}' which does not exist.",
                                rule="allowed_children",
                            )
                        )
                    elif child_comp.type not in def_item.allowed_children:
                        errors.append(
                            CompositionValidationError(
                                component_id=comp.id,
                                message=(
                                    f"Container '{comp.id}' of type '{comp.type}' does not allow child "
                                    f"'{child_id}' of type '{child_comp.type}'."
                                ),
                                rule="allowed_children",
                            )
                        )

    return errors
