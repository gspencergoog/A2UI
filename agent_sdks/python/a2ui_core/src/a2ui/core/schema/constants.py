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

from typing import Final, Literal, TypeAlias

SPEC_VERSION: Final = "v1.0"
SUPPORTED_VERSIONS: TypeAlias = Literal["v0.9", "v0.9.1", "v1.0"]
SUPPORTED_VERSIONS_TUPLE = ("v0.9", "v0.9.1", "v1.0")
SPEC_VERSION_TYPE: TypeAlias = SUPPORTED_VERSIONS
SPEC_BASE_URL = "https://a2ui.org/specification"

A2UI_MIME_TYPE: Final = "application/a2ui+json"
A2UI_MIME_TYPE_LEGACY: Final = "application/json+a2ui"


def is_a2ui_mime_type(mime_type: str) -> bool:
    """Checks if a given MIME type string matches A2UI canonical or legacy MIME type."""
    if not mime_type:
        return False
    normalized = mime_type.split(";")[0].strip().lower()
    return normalized in (A2UI_MIME_TYPE, A2UI_MIME_TYPE_LEGACY)


def is_supported_version(version: str) -> bool:
    """Checks if version string is a supported A2UI protocol version."""
    return version in SUPPORTED_VERSIONS_TUPLE


MSG_TYPE_CREATE_SURFACE = "createSurface"
MSG_TYPE_UPDATE_COMPONENTS = "updateComponents"
MSG_TYPE_UPDATE_DATA_MODEL = "updateDataModel"
MSG_TYPE_DELETE_SURFACE = "deleteSurface"
MSG_TYPE_CALL_RENDERER_FUNCTION = "callRendererFunction"
MSG_TYPE_AGENT_FUNCTION_RESPONSE = "agentFunctionResponse"
MSG_TYPE_CALL_AGENT_FUNCTION = "callAgentFunction"
MSG_TYPE_RENDERER_FUNCTION_RESPONSE = "rendererFunctionResponse"

CATALOG_COMPONENTS_KEY = "components"
SURFACE_ID_KEY = "surfaceId"
THEME_KEY = "theme"

ROOT_ID = "root"
