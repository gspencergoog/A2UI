"""Pydantic models and schemas for A2UI v1.0 Catalog Definitions."""

from typing import Dict, List, Literal, Optional, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator
from a2ui.core.validating.uax31 import is_valid_uax31_identifier


class ComponentDefinition(BaseModel):
    """Component definition model including composition constraints."""

    model_config = ConfigDict(extra="forbid")

    allowed_parents: Optional[List[str]] = Field(
        default=None,
        alias="allowedParents",
        description="List of allowed parent component types.",
    )
    allowed_children: Optional[List[str]] = Field(
        default=None,
        alias="allowedChildren",
        description="List of allowed child component types.",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional static metadata.",
    )


class FunctionDefinition(BaseModel):
    """Function definition model including returnType and callableFrom."""

    model_config = ConfigDict(extra="forbid")

    return_type: Literal[
        "string", "number", "boolean", "array", "object", "any", "void"
    ] = Field(
        alias="returnType",
        description="The type of value this function returns.",
    )
    callable_from: Literal["rendererOnly", "agentOnly", "rendererOrAgent"] = Field(
        default="rendererOnly",
        alias="callableFrom",
        description="Specifies where this function can be invoked from.",
    )
    requires_user_activation: bool = Field(
        default=False,
        alias="requiresUserActivation",
        description="Whether user activation context is required.",
    )
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class CatalogDefinition(BaseModel):
    """Catalog definition for A2UI v1.0."""

    model_config = ConfigDict(extra="forbid")

    protocol_version: Optional[str] = Field(
        default="1.0",
        alias="protocolVersion",
        description="A2UI specification version of this catalog.",
    )
    catalog_id: str = Field(
        alias="catalogId",
        description="Unique identifier for this catalog.",
    )
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    components: Optional[Dict[str, ComponentDefinition]] = None
    functions: Optional[Dict[str, FunctionDefinition]] = None

    @field_validator("components", mode="after")
    @classmethod
    def validate_component_names(
        cls, v: Optional[Dict[str, ComponentDefinition]]
    ) -> Optional[Dict[str, ComponentDefinition]]:
        """Ensures all component names are valid UAX #31 identifiers and not 'Surface'."""
        if v is not None:
            for name in v.keys():
                if name == "Surface":
                    raise ValueError("Component name cannot be 'Surface'")
                if not is_valid_uax31_identifier(name):
                    raise ValueError(
                        f"Component name '{name}' must be a valid UAX #31 identifier"
                    )
        return v

    @field_validator("functions", mode="after")
    @classmethod
    def validate_function_names(
        cls, v: Optional[Dict[str, FunctionDefinition]]
    ) -> Optional[Dict[str, FunctionDefinition]]:
        """Ensures all function names are valid UAX #31 identifiers."""
        if v is not None:
            for name in v.keys():
                if not is_valid_uax31_identifier(name):
                    raise ValueError(
                        f"Function name '{name}' must be a valid UAX #31 identifier"
                    )
        return v
