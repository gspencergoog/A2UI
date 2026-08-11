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

import json
from pathlib import Path
from typing import Any, Dict

SCHEMA_BASE_DIR = Path(__file__).parent


def get_schema_path(schema_name: str, version: str = "v1_0") -> Path:
    """Returns absolute Path to packaged JSON schema file.

    Args:
        schema_name: Name of schema file (e.g. 'agent_to_renderer.json' or 'agent_to_renderer')
        version: Spec version directory ('v1_0' or 'v0_9')
    """
    if not schema_name.endswith(".json"):
        schema_name = f"{schema_name}.json"
    ver_dir = version.replace(".", "_")
    path = SCHEMA_BASE_DIR / ver_dir / schema_name
    if not path.exists():
        raise FileNotFoundError(f"Schema asset not found: {path}")
    return path


def load_schema_json(schema_name: str, version: str = "v1_0") -> Dict[str, Any]:
    """Loads and returns raw parsed JSON schema dictionary from package assets."""
    path = get_schema_path(schema_name, version)
    with path.open("r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)
        return data
