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

from typing import Any, Dict, List, Optional
from pydantic import Field
from .common_types import StrictBaseModel


class RendererCapabilitiesV1_0(StrictBaseModel):
    supported_catalog_ids: List[str] = Field(..., alias="supportedCatalogIds")
    inline_catalogs: Optional[List[Dict[str, Any]]] = Field(
        None, alias="inlineCatalogs"
    )


class RendererCapabilities(StrictBaseModel):
    v1_0: Optional[RendererCapabilitiesV1_0] = Field(None, alias="v1.0")
    v0_9: Optional[RendererCapabilitiesV1_0] = Field(None, alias="v0.9")
    v0_9_1: Optional[RendererCapabilitiesV1_0] = Field(None, alias="v0.9.1")


# Backward compatibility aliases for client capabilities
A2uiClientCapabilities = RendererCapabilities
V09Capabilities = RendererCapabilitiesV1_0
