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

"""Prompt builder for the rizzcharts agent."""

# pylint: disable=g-importing-member, line-too-long
import os
from a2ui.core.schema.constants import VERSION_0_8, VERSION_0_9, SUPPORTED_VERSIONS
from a2ui.core.schema.manager import A2uiSchemaManager, CatalogConfig
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.core.schema.common_modifiers import remove_strict_validation
from agent import (
    ROLE_DESCRIPTION,
    WORKFLOW_DESCRIPTION,
    UI_DESCRIPTION_V0_8,
    UI_DESCRIPTION_V0_9,
)


if __name__ == "__main__":
  for my_version in SUPPORTED_VERSIONS:
    version_dir = f"v{my_version.replace('.', '_')}"
    ui_desc = UI_DESCRIPTION_V0_8 if my_version == VERSION_0_8 else UI_DESCRIPTION_V0_9

    schema_manager = A2uiSchemaManager(
        my_version,
        catalogs=[
            CatalogConfig.from_path(
                name="rizzcharts",
                catalog_path="rizzcharts_catalog_definition.json",
                examples_path=f"{version_dir}/examples/rizzcharts_catalog",
            ),
            BasicCatalog.get_config(
                version=my_version,
                examples_path=f"{version_dir}/examples/standard_catalog",
            ),
        ],
        accepts_inline_catalogs=True,
        schema_modifiers=[remove_strict_validation],
    )

    # Generate prompt for rizzcharts catalog
    print(f"Building prompt for version {my_version} and validating examples...")
    system_prompt = schema_manager.generate_system_prompt(
        role_description=ROLE_DESCRIPTION,
        workflow_description=WORKFLOW_DESCRIPTION,
        ui_description=ui_desc,
        include_schema=True,
        include_examples=True,
        validate_examples=True,
    )

    output = system_prompt

    # Also validate standard catalog examples
    print(f"Validating standard catalog examples for version {my_version}...")
    # We can trigger this by selecting the basic catalog
    basic_catalog_uri = (
        "https://a2ui.org/specification/v0_8/basic_catalog.json"
        if my_version == VERSION_0_8
        else "https://a2ui.org/specification/v0_9/basic_catalog.json"
    )
    std_prompt = schema_manager.generate_system_prompt(
        role_description=ROLE_DESCRIPTION,
        workflow_description=WORKFLOW_DESCRIPTION,
        ui_description=ui_desc,
        client_ui_capabilities={"supported_catalog_ids": [basic_catalog_uri]},
        include_schema=False,
        include_examples=True,
        validate_examples=True,
    )

    if std_prompt:
      output += "\n\n### Standard Catalog Examples:\n"
      # Find the start of examples in std_prompt
      if "### Examples:" in std_prompt:
        output += std_prompt.split("### Examples:")[1]

    filename = f"generated_prompt_{version_dir}.txt"
    with open(filename, "w") as f:
      f.write(output)
    print(f"Generated prompt saved to {filename}")
