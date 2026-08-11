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

import pytest
from pydantic import ValidationError

from a2ui.core.schema import (
    A2UI_MIME_TYPE,
    A2UI_MIME_TYPE_LEGACY,
    is_a2ui_mime_type,
    CreateSurfaceMessage,
    UpdateComponentsMessage,
    UpdateDataModelMessage,
    DeleteSurfaceMessage,
    CallRendererFunctionMessage,
    AgentFunctionResponseMessage,
    ActionMessage,
    CallAgentFunctionMessage,
    RendererFunctionResponseMessage,
    ErrorMessage,
    A2uiValidationError,
    A2uiGenericError,
    AgentCapabilities,
    RendererCapabilities,
    load_schema_json,
    get_schema_path,
)


def test_mime_type_constants_and_fallback():
    assert A2UI_MIME_TYPE == "application/a2ui+json"
    assert A2UI_MIME_TYPE_LEGACY == "application/json+a2ui"
    assert is_a2ui_mime_type("application/a2ui+json") is True
    assert is_a2ui_mime_type("application/json+a2ui") is True
    assert is_a2ui_mime_type("APPLICATION/A2UI+JSON; charset=utf-8") is True
    assert is_a2ui_mime_type("application/json") is False
    assert is_a2ui_mime_type("") is False


def test_schema_loader_assets():
    path = get_schema_path("agent_to_renderer")
    assert path.exists()
    schema_dict = load_schema_json("agent_to_renderer")
    assert schema_dict["title"] == "A2UI Message Schema"

    with pytest.raises(FileNotFoundError):
        get_schema_path("non_existent_schema_file")


def test_agent_to_renderer_v1_0_messages():
    # 1. createSurface
    cs_data = {
        "version": "v1.0",
        "createSurface": {
            "surfaceId": "surf_1",
            "catalogId": "cat_1",
            "sendDataModel": True,
            "components": [{"id": "root", "component": "Box"}],
            "dataModel": {"user": "Bob"},
        },
    }
    cs_msg = CreateSurfaceMessage.model_validate(cs_data)
    assert cs_msg.version == "v1.0"
    assert cs_msg.create_surface.surface_id == "surf_1"
    assert cs_msg.create_surface.data_model == {"user": "Bob"}

    # 2. callRendererFunction
    crf_data = {
        "version": "v1.0",
        "callRendererFunction": {
            "functionCallId": "call_1",
            "callFunction": {
                "call": "getGeoLocation",
                "catalogId": "basic",
                "args": {"accuracy": "high"},
            },
        },
    }
    crf_msg = CallRendererFunctionMessage.model_validate(crf_data)
    assert crf_msg.call_renderer_function.function_call_id == "call_1"

    # Fails if callRendererFunction is missing catalogId
    with pytest.raises(ValidationError):
        CallRendererFunctionMessage.model_validate({
            "version": "v1.0",
            "callRendererFunction": {
                "functionCallId": "call_1",
                "callFunction": {"call": "getGeoLocation"},
            },
        })

    # 3. agentFunctionResponse (value)
    afr_value = {
        "version": "v1.0",
        "agentFunctionResponse": {
            "functionCallId": "call_1",
            "value": {"lat": 1.23, "lng": 4.56},
        },
    }
    afr_val_msg = AgentFunctionResponseMessage.model_validate(afr_value)
    assert afr_val_msg.agent_function_response.value == {"lat": 1.23, "lng": 4.56}

    # 4. agentFunctionResponse (error)
    afr_err = {
        "version": "v1.0",
        "agentFunctionResponse": {
            "functionCallId": "call_1",
            "error": {"code": "DENIED", "message": "Permission denied"},
        },
    }
    afr_err_msg = AgentFunctionResponseMessage.model_validate(afr_err)
    assert afr_err_msg.agent_function_response.error.code == "DENIED"

    # Fails if both value and error present
    with pytest.raises(ValidationError):
        AgentFunctionResponseMessage.model_validate({
            "version": "v1.0",
            "agentFunctionResponse": {
                "functionCallId": "call_1",
                "value": "ok",
                "error": {"code": "ERR", "message": "fail"},
            },
        })


def test_renderer_to_agent_v1_0_messages():
    # 1. action
    act_data = {
        "version": "v1.0",
        "action": {
            "name": "click",
            "surfaceId": "s1",
            "sourceComponentId": "btn1",
            "timestamp": "2026-08-11T10:00:00Z",
            "context": {"key": "val"},
        },
    }
    act_msg = ActionMessage.model_validate(act_data)
    assert act_msg.action.name == "click"

    # 2. callAgentFunction
    caf_data = {
        "version": "v1.0",
        "callAgentFunction": {
            "surfaceId": "s1",
            "functionCallId": "func_1",
            "callFunction": {"call": "doCalc"},
        },
    }
    caf_msg = CallAgentFunctionMessage.model_validate(caf_data)
    assert caf_msg.call_agent_function.function_call_id == "func_1"

    # 3. rendererFunctionResponse
    rfr_data = {
        "version": "v1.0",
        "rendererFunctionResponse": {
            "functionCallId": "call_1",
            "value": "res",
        },
    }
    rfr_msg = RendererFunctionResponseMessage.model_validate(rfr_data)
    assert rfr_msg.renderer_function_response.value == "res"


def test_error_schema_mutual_exclusivity():
    # 1. Surface-level error (valid)
    err_surf = ErrorMessage.model_validate({
        "version": "v1.0",
        "error": {
            "code": "RENDER_ERROR",
            "message": "Render failed",
            "surfaceId": "surf_1",
        },
    })
    assert isinstance(err_surf.error, A2uiGenericError)
    assert err_surf.error.surface_id == "surf_1"

    # 2. FunctionCall-level error (valid)
    err_func = ErrorMessage.model_validate({
        "version": "v1.0",
        "error": {
            "code": "EXEC_ERROR",
            "message": "Exec failed",
            "functionCallId": "call_1",
        },
    })
    assert isinstance(err_func.error, A2uiGenericError)
    assert err_func.error.function_call_id == "call_1"

    # 3. Error with BOTH surfaceId and functionCallId (FAILS validation)
    with pytest.raises(
        ValidationError, match="cannot specify both surfaceId and functionCallId"
    ):
        ErrorMessage.model_validate({
            "version": "v1.0",
            "error": {
                "code": "AMBIGUOUS_ERROR",
                "message": "Conflict",
                "surfaceId": "surf_1",
                "functionCallId": "call_1",
            },
        })

    # 4. Error with NEITHER surfaceId nor functionCallId (FAILS validation)
    with pytest.raises(
        ValidationError, match="must specify either surfaceId or functionCallId"
    ):
        ErrorMessage.model_validate({
            "version": "v1.0",
            "error": {
                "code": "MISSING_ID_ERROR",
                "message": "Missing ID",
            },
        })

    # 5. Generic error using VALIDATION_FAILED code (FAILS validation)
    with pytest.raises(ValidationError, match="reserved for validation errors"):
        ErrorMessage.model_validate({
            "version": "v1.0",
            "error": {
                "code": "VALIDATION_FAILED",
                "message": "Wrong type",
                "surfaceId": "surf_1",
            },
        })


def test_unknown_version_rejection():
    with pytest.raises(ValidationError):
        CreateSurfaceMessage.model_validate({
            "version": "v0.8",
            "createSurface": {"surfaceId": "s1"},
        })

    with pytest.raises(ValidationError):
        ActionMessage.model_validate({
            "version": "v2.0",
            "action": {
                "name": "a",
                "surfaceId": "s1",
                "sourceComponentId": "c1",
                "timestamp": "2026-08-11T10:00:00Z",
                "context": {},
            },
        })


def test_capabilities_models():
    agent_caps = AgentCapabilities.model_validate(
        {
            "v1.0": {
                "supportedCatalogIds": ["basic"],
                "acceptsInlineCatalogs": True,
            }
        }
    )
    assert agent_caps.v1_0.accepts_inline_catalogs is True

    renderer_caps = RendererCapabilities.model_validate({
        "v1.0": {
            "supportedCatalogIds": ["basic"],
            "inlineCatalogs": [{"catalogId": "inline1"}],
        }
    })
    assert renderer_caps.v1_0.supported_catalog_ids == ["basic"]
