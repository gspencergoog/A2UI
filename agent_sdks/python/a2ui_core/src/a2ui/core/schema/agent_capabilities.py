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


class AgentCapabilitiesV1_0(StrictBaseModel):
    supported_catalog_ids: Optional[List[str]] = Field(
        None, alias="supportedCatalogIds"
    )
    accepts_inline_catalogs: Optional[bool] = Field(
        False, alias="acceptsInlineCatalogs"
    )


class AgentCapabilitiesV0_9(StrictBaseModel):
    supported_catalog_ids: Optional[List[str]] = Field(
        None, alias="supportedCatalogIds"
    )
    accepts_inline_catalogs: Optional[bool] = Field(
        False, alias="acceptsInlineCatalogs"
    )


class AgentCapabilities(StrictBaseModel):
    v1_0: Optional[AgentCapabilitiesV1_0] = Field(None, alias="v1.0")
    v0_9: Optional[AgentCapabilitiesV0_9] = Field(None, alias="v0.9")
    v0_9_1: Optional[AgentCapabilitiesV0_9] = Field(None, alias="v0.9.1")
