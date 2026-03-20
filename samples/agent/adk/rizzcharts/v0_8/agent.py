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

import os
from typing import Any
from a2ui.core.schema.constants import VERSION_0_8
from a2ui.core.schema.manager import A2uiSchemaManager, CatalogConfig
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.adk.a2a_extension.send_a2ui_to_client_toolset import (
    A2uiEnabledProvider,
    A2uiCatalogProvider,
    A2uiExamplesProvider,
)
from ..agent import RizzchartsAgent, UI_DESCRIPTION_V0_8

class RizzchartsAgentV08(RizzchartsAgent):
  """Rizzcharts Agent specialized for A2UI v0.8."""

  def __init__(
      self,
      model: Any,
      base_url: str,
      a2ui_enabled_provider: A2uiEnabledProvider,
      a2ui_catalog_provider: A2uiCatalogProvider,
      a2ui_examples_provider: A2uiExamplesProvider,
  ):
    v_dir = os.path.dirname(__file__)
    schema_manager = A2uiSchemaManager(
        VERSION_0_8,
        catalogs=[
            CatalogConfig.from_path(
                name="rizzcharts",
                catalog_path=os.path.join(os.path.dirname(v_dir), "rizzcharts_catalog_definition.json"),
                examples_path=os.path.join(v_dir, "examples", "rizzcharts_catalog"),
            ),
            BasicCatalog.get_config(
                version=VERSION_0_8,
                examples_path=os.path.join(v_dir, "examples", "standard_catalog"),
            ),
        ],
        accepts_inline_catalogs=True,
    )
    super().__init__(
        model=model,
        base_url=base_url,
        version=VERSION_0_8,
        ui_description=UI_DESCRIPTION_V0_8,
        schema_manager=schema_manager,
        a2ui_enabled_provider=a2ui_enabled_provider,
        a2ui_catalog_provider=a2ui_catalog_provider,
        a2ui_examples_provider=a2ui_examples_provider,
    )
