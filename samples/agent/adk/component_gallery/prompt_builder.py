# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A simple script to verify the Component Gallery JSON generation."""

import asyncio
import os
import sys

# Add the path to the ADK and A2UI SDK
sys.path.append(os.path.abspath("../../../../agent_sdks/python/src"))

from a2ui.core.schema.manager import A2uiSchemaManager
from a2ui.core.schema.validator import A2uiValidator
from a2ui.basic_catalog.provider import BasicCatalog
from gallery_examples import get_gallery_json

async def verify_gallery():
  for version in ["0.8", "0.9"]:
    print(f"\n--- VERIFYING VERSION {version} ---\n")
    schema_manager = A2uiSchemaManager(
        version=version,
        catalogs=[BasicCatalog.get_config(version=version)],
    )
    selected_catalog = schema_manager.get_selected_catalog()
    validator = A2uiValidator(selected_catalog)
    
    gallery_json = get_gallery_json(version=version)
    
    # Simple validation check
    try:
      # We just check if it parses and is a list
      import json
      data = json.loads(gallery_json)
      if not isinstance(data, list):
        print(f"Error: Gallery JSON for {version} is not a list")
        continue
      
      # Use validator to validate
      validator.validate(data)
      print(f"SUCCESS: Gallery JSON for {version} is valid.")
      
    except Exception as e:
      print(f"FAILED: Validation error for {version}: {e}")

if __name__ == "__main__":
  asyncio.run(verify_gallery())
