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


class CreateSurface(StrictBaseModel):
    surface_id: str = Field(
        ...,
        alias="surfaceId",
        description="The unique identifier for the UI surface to be rendered.",
    )
    catalog_id: Optional[str] = Field(
        None,
        alias="catalogId",
        description="A string that uniquely identifies the catalog.",
    )
    theme: Optional[Any] = Field(
        None,
        description="Theme parameters for the surface.",
    )
    send_data_model: Optional[bool] = Field(
        None,
        alias="sendDataModel",
        description="If true, the renderer will send full data model in A2A metadata.",
    )
    components: Optional[List[Any]] = Field(
        None,
        description="Initial component tree for the surface.",
    )
    data_model: Optional[Dict[str, Any]] = Field(
        None,
        alias="dataModel",
        description="Initial root data model object.",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional surface-level metadata.",
    )


class CreateSurfaceMessage(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    create_surface: CreateSurface = Field(..., alias="createSurface")


class UpdateComponents(StrictBaseModel):
    surface_id: str = Field(
        ...,
        alias="surfaceId",
        description="The unique identifier for the UI surface to be updated.",
    )
    components: List[Any] = Field(
        ...,
        min_length=1,
        description="A list containing all UI components for the surface.",
    )


class UpdateComponentsMessage(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    update_components: UpdateComponents = Field(..., alias="updateComponents")


class UpdateDataModel(StrictBaseModel):
    surface_id: str = Field(
        ...,
        alias="surfaceId",
        description="The unique identifier for the UI surface this update applies to.",
    )
    path: Optional[str] = Field(
        None,
        description="An optional path to a location within the data model.",
    )
    value: Any = Field(
        ...,
        description="The data to be updated in the data model.",
    )


class UpdateDataModelMessage(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    update_data_model: UpdateDataModel = Field(..., alias="updateDataModel")


class DeleteSurface(StrictBaseModel):
    surface_id: str = Field(
        ...,
        alias="surfaceId",
        description="The unique identifier for the UI surface to be deleted.",
    )


class DeleteSurfaceMessage(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    delete_surface: DeleteSurface = Field(..., alias="deleteSurface")


class CallFunction(StrictBaseModel):
    call: str = Field(..., description="The name of the function to call.")
    catalog_id: str = Field(
        ..., alias="catalogId", description="Catalog ID for the function."
    )
    args: Optional[Dict[str, Any]] = Field(None, description="Function arguments.")


class CallRendererFunction(StrictBaseModel):
    function_call_id: str = Field(
        ...,
        alias="functionCallId",
        description="Unique ID for this instance of function call.",
    )
    call_function: CallFunction = Field(..., alias="callFunction")


class CallRendererFunctionMessage(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    call_renderer_function: CallRendererFunction = Field(
        ..., alias="callRendererFunction"
    )


class FunctionResponseError(StrictBaseModel):
    code: str = Field(...)
    message: str = Field(...)


class FunctionResponsePayload(StrictBaseModel):
    function_call_id: str = Field(..., alias="functionCallId")
    value: Optional[Any] = Field(None)
    error: Optional[FunctionResponseError] = Field(None)

    @model_validator(mode="after")
    def validate_one_of(self) -> "FunctionResponsePayload":
        if self.value is not None and self.error is not None:
            raise ValueError("FunctionResponse cannot contain both value and error.")
        if self.value is None and self.error is None:
            raise ValueError("FunctionResponse must contain either value or error.")
        return self


class AgentFunctionResponseMessage(StrictBaseModel):
    version: SUPPORTED_VERSIONS = SPEC_VERSION
    agent_function_response: FunctionResponsePayload = Field(
        ..., alias="agentFunctionResponse"
    )


AgentToRendererMessage = Union[
    CreateSurfaceMessage,
    UpdateComponentsMessage,
    UpdateDataModelMessage,
    DeleteSurfaceMessage,
    CallRendererFunctionMessage,
    AgentFunctionResponseMessage,
]

# Backward compatibility aliases
ServerToClientMessage = AgentToRendererMessage
A2uiMessage = AgentToRendererMessage


class AgentToRendererMessageListWrapper(StrictBaseModel):
    messages: List[AgentToRendererMessage] = Field(
        ..., description="A list of Agent-to-Renderer messages."
    )


A2uiMessageListWrapper = AgentToRendererMessageListWrapper
