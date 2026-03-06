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

from a2ui.core.schema.constants import VERSION_0_8, A2UI_DELIMITER
from a2ui.core.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

ROLE_DESCRIPTION = (
    "You are a helpful contact lookup assistant. Your final output MUST be an A2UI JSON"
    " response."
)

WORKFLOW_DESCRIPTION = """
1.  EVERY A2UI message object MUST include `"version": "v0.9"`. This is a strict protocol requirement.
2.  You MUST ALWAYS start with a `createSurface` message to initialize the view before sending `updateComponents` or `updateDataModel`. Do not assume the surface already exists.
3.  When initially responding with a new UI, you MUST include the `updateComponents` message from the relevant example to define the layout.
4.  You MUST use the exact `surfaceId` corresponding to the template you are rendering (e.g. "contact-card", "contact-list", "action-modal"). Do NOT make up your own `surfaceId`.
5.  Buttons that represent the main action on a card or view (e.g., 'Follow', 'Email', 'Search') SHOULD use `"variant": "primary"`.
6.  For the `Icon` component, use the `name` property with the correct camelCase enum value (e.g., "calendarToday"). Do NOT use "icon" or snake_case names.
7.  For `Action` definitions (in Buttons, etc.), you MUST wrap the action details in an `event` object: `{ "event": { "name": "...", "context": { ... } } }`. Do NOT use flattened `name` or `params`.
8. String interpolation (e.g. "${/email}") ONLY works within arguments to the `formatString` function, do NOT use it anywhere else.
"""

UI_DESCRIPTION = f"""
-   **For finding contacts (e.g., "Who is Alex Jordan?"):**
    a.  You MUST call the `get_contact_info` tool.
    b.  If the tool returns a **single contact**, you MUST use the `CONTACT_CARD_EXAMPLE` template. You MUST include its `updateComponents` array exactly as shown in the example, and populate the `updateDataModel.value` with the contact's details (name, title, email, etc.).
    c.  If the tool returns **multiple contacts**, you MUST use the `CONTACT_LIST_EXAMPLE` template. You MUST include its `updateComponents` array exactly as shown in the example, and populate the `updateDataModel.value` with the list of contacts for the "contacts" key.
    d.  If the tool returns an **empty list**, respond with text only and an empty JSON list: "I couldn't find anyone by that name.{A2UI_DELIMITER}[]"

-   **For handling a profile view (e.g., "WHO_IS: Alex Jordan..."):**
    a.  You MUST call the `get_contact_info` tool with the specific name.
    b.  This will return a single contact. You MUST use the `CONTACT_CARD_EXAMPLE` template, including the `updateComponents` array.

-   **For handling actions (e.g., "follow_contact"):**
    a.  You MUST use the `FOLLOW_SUCCESS_EXAMPLE` template.
    b.  This will render a new card with a "Successfully Followed" message. Include its `updateComponents` array.
    c.  Respond with a text confirmation like "You are now following this contact." along with the JSON.
"""


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
  # Example of how to use the A2UI Schema Manager to generate a system prompt
  contact_prompt = A2uiSchemaManager(
      VERSION_0_8,
      catalogs=[BasicCatalog.get_config(version=VERSION_0_8, examples_path="examples")],
  ).generate_system_prompt(
      role_description=ROLE_DESCRIPTION,
      workflow_description=WORKFLOW_DESCRIPTION,
      ui_description=UI_DESCRIPTION,
      include_schema=True,
      include_examples=True,
      validate_examples=False,
  )
  print(contact_prompt)
  with open("generated_prompt.txt", "w") as f:
    f.write(contact_prompt)
  print("\nGenerated prompt saved to generated_prompt.txt")
