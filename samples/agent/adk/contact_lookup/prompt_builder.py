# Copyright 2025 Google LLC
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
from a2ui.core.schema.constants import (
    VERSION_0_8,
    VERSION_0_9,
    A2UI_OPEN_TAG,
    A2UI_CLOSE_TAG,
)
from a2ui.core.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

ROLE_DESCRIPTION = (
    "You are a helpful contact lookup assistant. Your final output MUST be an A2UI JSON"
    " response."
)

WORKFLOW_DESCRIPTION = f"""
To generate the response, you MUST follow these rules:
1.  Your response can contain one or more A2UI JSON blocks.
2.  Each A2UI JSON block MUST be wrapped in `{A2UI_OPEN_TAG}` and `{A2UI_CLOSE_TAG}` tags.
3.  Between or around these blocks, you can provide conversational text.
4.  The JSON part MUST be a single, raw JSON object (usually a list of A2UI messages) and MUST validate against the provided A2UI JSON SCHEMA.
"""

UI_DESCRIPTION_V0_8 = f"""
-   **For finding contacts (e.g., "Who is Alex Jordan?"):**
    a.  You MUST call the `get_contact_info` tool.
    b.  If the tool returns a **single contact**, you MUST use the `CONTACT_CARD` component. Populate the `dataModelUpdate.value` with the contact's details.
    c.  If the tool returns **multiple contacts**, you MUST use the `CONTACT_LIST` component. Populate the `dataModelUpdate.value` with the list of contacts for the "contacts" key.
    d.  If the tool returns an **empty list**, respond with text only and an empty JSON list: "I couldn't find anyone by that name. {A2UI_OPEN_TAG}[]{A2UI_CLOSE_TAG}"
"""

UI_DESCRIPTION_V0_9 = f"""
-   **For finding contacts (e.g., "Who is Alex Jordan?"):**
    a.  You MUST call the `get_contact_info` tool.
    b.  If the tool returns a **single contact**, you MUST use the `CONTACT_CARD` component. Populate the `updateDataModel.value` with the contact's details.
    c.  If the tool returns **multiple contacts**, you MUST use the `CONTACT_LIST` component. Populate the `updateDataModel.value` with the list of contacts for the "contacts" key.
    d.  If the tool returns an **empty list**, respond with text only and an empty JSON list: "I couldn't find anyone by that name. {A2UI_OPEN_TAG}[]{A2UI_CLOSE_TAG}"
"""

# Keep the original for backward compatibility during refactoring if needed
UI_DESCRIPTION = UI_DESCRIPTION_V0_9


def get_text_prompt() -> str:
  """
  Constructs the prompt for a text-only agent.
  """
  return """
    You are a helpful contact lookup assistant. Your final output MUST be a text response.

    To generate the response, you MUST follow these rules:
    1.  **For finding contacts:**
        a. You MUST call the `get_contact_info` tool. Extract the name and department from the user's query.
        b. After receiving the data, format the contact(s) as a clear, human-readable text response.
        c. If multiple contacts are found, list their names and titles.
        d. If one contact is found, list all their details.

    2.  **For handling actions (e.g., "USER_WANTS_TO_EMAIL: ..."):**
        a. Respond with a simple text confirmation (e.g., "Drafting an email to...").
    """


if __name__ == "__main__":
  SUPPORTED_VERSIONS = [VERSION_0_9, VERSION_0_8]
  for version in SUPPORTED_VERSIONS:
    print(f"\n{'='*20} Generating Prompt for A2UI v{version} {'='*20}")
    ui_desc = UI_DESCRIPTION_V0_9 if version == VERSION_0_9 else UI_DESCRIPTION_V0_8
    
    # Use relative path for examples to match directory structure
    examples_rel_path = f"v{version.replace('.', '_')}/examples"
    examples_path = os.path.join(os.path.dirname(__file__), examples_rel_path)
    
    contact_prompt = A2uiSchemaManager(
        version,
        catalogs=[
            BasicCatalog.get_config(
                version=version,
                examples_path=examples_path,
            )
        ],
    ).generate_system_prompt(
        role_description=ROLE_DESCRIPTION,
        workflow_description=WORKFLOW_DESCRIPTION,
        ui_description=ui_desc,
        include_schema=True,
        include_examples=True,
        validate_examples=False,
    )
    
    out_file = f"generated_prompt_v{version.replace('.', '_')}.txt"
    with open(out_file, "w") as f:
      f.write(contact_prompt)
    print(f"Generated prompt saved to {out_file}")
