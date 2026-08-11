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

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, ConfigDict, model_validator

from .common_types import StrictBaseModel
from .constants import SPEC_VERSION, SUPPORTED_VERSIONS
from .agent_to_renderer import FunctionResponsePayload


class A2uiClientAction(StrictBaseModel):
    name: str = Field(
        ...,
        description="The name of the action from component's action.event.name.",
    )
    surface_id: str = Field(
        ...,
        alias="surfaceId",
        description="The id of the surface where event originated.",
    )
    source_component_id: str = Field(
        ...,
        alias="sourceComponentId",
        description="The id of the component that triggered event.",
    )
    timestamp: str = Field(
        ..., description="An ISO 8601 timestamp of when event occurred."
    )
    context: Dict[str, Any] = Field(
        ...,
        description="JSON object containing key-value pairs after binding resolution.",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional action metadata."
    )


class A2uiValidationError(StrictBaseModel):
    code: Literal["VALIDATION_FAILED", "UNALLOWED_PARENT", "UNALLOWED_CHILD"] = Field(
        "VALIDATION_FAILED"
    )
    surface_id: str = Field(
        ...,
        alias="surfaceId",
        description="The id of the surface where error occurred.",
    )
    path: str = Field(
        ...,
        description="JSON pointer to field that failed validation.",
    )
    message: str = Field(
        ...,
        description="Short description of why validation failed.",
    )


class A2uiGenericError(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    code: str = Field(...)
    message: str = Field(..., description="Short description of error.")
    surface_id: Optional[str] = Field(None, alias="surfaceId")
    function_call_id: Optional[str] = Field(None, alias="functionCallId")

    @model_validator(mode="after")
    def check_mutual_exclusivity(self) -> "A2uiGenericError":
        if self.code in ("VALIDATION_FAILED", "UNALLOWED_PARENT", "UNALLOWED_CHILD"):
            raise ValueError(f"Code '{self.code}' is reserved for validation errors.")
        if self.surface_id is not None and self.function_call_id is not None:
            raise ValueError(
                "Generic error cannot specify both surfaceId and functionCallId."
            )
        if self.surface_id is None and self.function_call_id is None:
            raise ValueError(
                "Generic error must specify either surfaceId or functionCallId."
            )
        return self


A2uiClientError = Union[A2uiValidationError, A2uiGenericError]


class ActionMessage(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    action: A2uiClientAction = Field(...)


A2uiClientActionMessage = ActionMessage


class AgentCallFunction(StrictBaseModel):
    call: str = Field(..., description="The name of the function to call.")
    catalog_id: Optional[str] = Field(None, alias="catalogId")
    args: Optional[Dict[str, Any]] = Field(None, description="Function arguments.")


class CallAgentFunction(StrictBaseModel):
    surface_id: str = Field(..., alias="surfaceId")
    function_call_id: str = Field(..., alias="functionCallId")
    call_function: AgentCallFunction = Field(..., alias="callFunction")


class CallAgentFunctionMessage(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    call_agent_function: CallAgentFunction = Field(..., alias="callAgentFunction")


class RendererFunctionResponseMessage(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    renderer_function_response: FunctionResponsePayload = Field(
        ..., alias="rendererFunctionResponse"
    )


class ErrorMessage(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    error: A2uiClientError = Field(...)


A2uiClientErrorMessage = ErrorMessage

RendererToAgentMessage = Union[
    ActionMessage,
    CallAgentFunctionMessage,
    RendererFunctionResponseMessage,
    ErrorMessage,
]

# Backward compatibility aliases
ClientToServerMessage = RendererToAgentMessage
A2uiClientMessage = RendererToAgentMessage


class A2uiClientDataModel(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    surfaces: Dict[str, Dict[str, Any]] = Field(
        ..., description="A map of surface IDs to their current data models."
    )


A2uiClientMessageList = List[RendererToAgentMessage]


class A2uiClientMessageListWrapper(StrictBaseModel):
    messages: A2uiClientMessageList = Field(
        ..., description="Object wrapping list of messages."
    )
