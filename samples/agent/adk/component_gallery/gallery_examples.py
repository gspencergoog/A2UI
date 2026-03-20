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

"""Defines the Component Gallery 'Kitchen Sink' example."""

import json


def get_gallery_json(version: str = "0.9") -> str:
  """Returns the JSON structure for the Component Gallery surfaces.

  Args:
      version: The A2UI version to use ("0.8" or "0.9").
  """

  messages = []

  def wrap_component(comp_id: str, comp_def: dict[str, Any]) -> dict[str, Any]:
    """Wraps a component definition according to the specified protocol version."""
    if version == "0.8":
      return {"id": comp_id, "component": comp_def}
    else:
      # v0.9 Modular Catalog style
      type_name = list(comp_def.keys())[0]
      props = comp_def[type_name]
      return {"id": comp_id, "component": type_name, **props}

  # Helper to create a surface for one or more components
  def add_demo_surface(surface_id, definitions):
    # v0.9 requires one component with id "root". 
    # v0.8 doesn't require it but it's good practice.
    root_id = "root" if version == "0.8" else "root" 
    # Actually, v0.8 beginRendering specifies the root ID, so it can be anything.
    # But v0.9 updateComponents requires ONE component with id "root".
    # Let's just use "root" for both to be safe and simple.
    root_id = "root"
    
    # 1. Determine the component definition for this version
    comp_def = None
    if isinstance(definitions, dict):
        comp_def = definitions.get(version)
    
    if comp_def is None:
        comp_def = definitions

    # 2. Add components to the surface
    components = []
    if isinstance(comp_def, list):
        # List of (id, definition) tuples
        for cid, cdef in comp_def:
            components.append(wrap_component(cid, cdef))
    elif isinstance(comp_def, dict):
        # Single component definition
        components.append(wrap_component(root_id, comp_def))
    else:
        raise ValueError(f"Invalid component definition type: {type(comp_def)}")

    if version == "0.8":
      messages.append({"beginRendering": {"surfaceId": surface_id, "root": root_id}})
      messages.append(
          {"surfaceUpdate": {"surfaceId": surface_id, "components": components}}
      )
      # Inject data model for this surface
      messages.append({
          "dataModelUpdate": {
              "surfaceId": surface_id,
              "path": "/galleryData",
              "contents": [
                  {"key": "textField", "valueString": "Hello World"},
                  {"key": "checkbox", "valueBoolean": False},
                  {"key": "checkboxChecked", "valueBoolean": True},
                  {"key": "slider", "valueNumber": 30},
                  {"key": "date", "valueString": "2025-10-26"},
                  {
                      "key": "favorites",
                      "valueMap": [{"key": "0", "valueString": "A"}],
                  },
                  {"key": "favoritesChips", "valueMap": []},
                  {"key": "favoritesFilter", "valueMap": []},
              ],
          }
      })
    else:
      messages.append({
          "version": "v0.9",
          "createSurface": {
              "surfaceId": surface_id,
              "catalogId": "https://a2ui.org/specification/v0_9/basic_catalog.json",
          },
      })
      messages.append({
          "version": "v0.9",
          "updateComponents": {"surfaceId": surface_id, "components": components},
      })
      # Inject data model for this surface
      messages.append({
          "version": "v0.9",
          "updateDataModel": {
              "surfaceId": surface_id,
              "value": {
                  "galleryData": {
                      "textField": "Hello World",
                      "checkbox": False,
                      "checkboxChecked": True,
                      "slider": 30,
                      "date": "2025-10-26",
                      "favorites": ["A"],
                      "favoritesChips": [],
                      "favoritesFilter": [],
                  }
              },
          },
      })

  # 1. TextField
  add_demo_surface(
      "demo-text",
      {
          "0.8": {
              "TextField": {
                  "label": {"literalString": "Enter some text"},
                  "text": { "path": "/galleryData/textField"},
              }
          },
          "0.9": {
              "TextField": {
                  "label": "Enter some text",
                  "value": { "path": "/galleryData/textField"},
              }
          },
      },
  )

  # 1b. TextField (Regex)
  add_demo_surface(
      "demo-text-regex",
      {
          "0.8": {
              "TextField": {
                  "label": {"literalString": "Enter exactly 5 digits"},
                  "text": { "path": "/galleryData/textFieldRegex"},
                  "validationRegexp": "^\\d{5}$",
              }
          },
          "0.9": {
              "TextField": {
                  "label": "Enter exactly 5 digits",
                  "value": { "path": "/galleryData/textFieldRegex"},
                  "validationRegexp": "^\\d{5}$",
              }
          },
      },
  )

  # 2. CheckBox
  add_demo_surface(
      "demo-checkbox",
      {
          "CheckBox": {
              "label": "Toggle me" if version == "0.9" else {"literalString": "Toggle me"},
              "value": { "path": "/galleryData/checkbox"},
          }
      },
  )

  # 3. Slider
  add_demo_surface(
      "demo-slider",
      {
          "0.8": {
              "Slider": {
                  "value": { "path": "/galleryData/slider"},
                  "minValue": 0,
                  "maxValue": 100,
              }
          },
          "0.9": {
              "Slider": {
                  "value": { "path": "/galleryData/slider"},
                  "min": 0,
                  "max": 100,
              }
          },
      },
  )

  # 4. DateTimeInput
  add_demo_surface(
      "demo-date",
      {
          "0.8": {
              "DateTimeInput": {"value": { "path": "/galleryData/date"}, "enableDate": True}
          },
          "0.9": {
              "DateTimeInput": {"value": { "path": "/galleryData/date"}, "enableDate": True}
          },
      },
  )

  # 5. ChoicePicker / MultipleChoice (Default)
  add_demo_surface(
      "demo-multichoice",
      {
          "0.8": {
              "MultipleChoice": {
                  "selections": { "path": "/galleryData/favorites"},
                  "options": [
                      {"label": {"literalString": "Apple"}, "value": "A"},
                      {"label": {"literalString": "Banana"}, "value": "B"},
                      {"label": {"literalString": "Cherry"}, "value": "C"},
                  ],
              }
          },
          "0.9": {
              "ChoicePicker": {
                  "value": { "path": "/galleryData/favorites"},
                  "variant": "multipleSelection",
                  "options": [
                      {"label": "Apple", "value": "A"},
                      {"label": "Banana", "value": "B"},
                      {"label": "Cherry", "value": "C"},
                  ],
              }
          },
      },
  )

  # 5b. MultipleChoice (Chips)
  add_demo_surface(
      "demo-multichoice-chips",
      {
          "0.8": {
              "MultipleChoice": {
                  "selections": { "path": "/galleryData/favoritesChips"},
                  "variant": "chips",
                  "options": [
                      {"label": {"literalString": "Work"}, "value": "work"},
                      {"label": {"literalString": "Home"}, "value": "home"},
                      {"label": {"literalString": "Urgent"}, "value": "urgent"},
                      {"label": {"literalString": "Later"}, "value": "later"},
                  ],
              }
          },
          "0.9": {
              "ChoicePicker": {
                  "value": { "path": "/galleryData/favoritesChips"},
                  "variant": "multipleSelection",
                  "displayStyle": "chips",
                  "options": [
                      {"label": "Work", "value": "work"},
                      {"label": "Home", "value": "home"},
                      {"label": "Urgent", "value": "urgent"},
                      {"label": "Later", "value": "later"},
                  ],
              }
          },
      },
  )

  # 5c. MultipleChoice (Filterable)
  add_demo_surface(
      "demo-multichoice-filter",
      {
          "0.8": {
              "MultipleChoice": {
                  "selections": { "path": "/galleryData/favoritesFilter"},
                  "filterable": True,
                  "options": [
                      {"label": {"literalString": "United States"}, "value": "US"},
                      {"label": {"literalString": "Canada"}, "value": "CA"},
                      {"label": {"literalString": "United Kingdom"}, "value": "UK"},
                      {"label": {"literalString": "Australia"}, "value": "AU"},
                      {"label": {"literalString": "Germany"}, "value": "DE"},
                      {"label": {"literalString": "France"}, "value": "FR"},
                      {"label": {"literalString": "Japan"}, "value": "JP"},
                  ],
              }
          },
          "0.9": {
              "ChoicePicker": {
                  "value": { "path": "/galleryData/favoritesFilter"},
                  "variant": "multipleSelection",
                  "filterable": True,
                  "options": [
                      {"label": "United States", "value": "US"},
                      {"label": "Canada", "value": "CA"},
                      {"label": "United Kingdom", "value": "UK"},
                      {"label": "Australia", "value": "AU"},
                      {"label": "Germany", "value": "DE"},
                      {"label": "France", "value": "FR"},
                      {"label": "Japan", "value": "JP"},
                  ],
              }
          },
      },
  )

  # 6. Image
  add_demo_surface(
      "demo-image",
      {
          "0.8": {
              "Image": {
                  "url": {"literalString": "http://localhost:10005/assets/a2ui.png"},
                  "usageHint": "mediumFeature",
              }
          },
          "0.9": {
              "Image": {
                  "url": "http://localhost:10005/assets/a2ui.png",
                  "variant": "mediumFeature",
              }
          },
      },
  )

  # 7. Button
  add_demo_surface(
      "demo-button",
      {
          "0.8": [
              ("demo-button-text", {"Text": {"text": {"literalString": "Trigger Action"}}}),
              (
                  "root",
                  {
                      "Button": {
                          "child": "demo-button-text",
                          "primary": True,
                          "action": {
                              "name": "custom_action",
                              "context": [{
                                  "key": "info",
                                  "value": {"literalString": "Custom Button Clicked"},
                              }],
                          },
                      }
                  },
              ),
          ],
          "0.9": [
              ("demo-button-text", {"Text": {"text": "Trigger Action"}}),
              (
                  "root",
                  {
                      "Button": {
                          "child": "demo-button-text",
                          "variant": "primary",
                          "action": {
                              "event": {
                                  "name": "custom_action",
                                  "context": {
                                      "info": "Custom Button Clicked"
                                  }
                              }
                          },
                      }
                  },
              ),
          ],
      },
  )

  # 8. Tabs
  add_demo_surface(
      "demo-tabs",
      {
          "0.8": [
              ("tab-1-content", {"Text": {"text": {"literalString": "First Tab Content"}}}),
              ("tab-2-content", {"Text": {"text": {"literalString": "Second Tab Content"}}}),
              (
                  "root",
                  {
                      "Tabs": {
                          "tabItems": [
                              {"title": {"literalString": "View One"}, "child": "tab-1-content"},
                              {"title": {"literalString": "View Two"}, "child": "tab-2-content"},
                          ]
                      }
                  },
              ),
          ],
          "0.9": [
              ("tab-1-content", {"Text": {"text": "First Tab Content"}}),
              ("tab-2-content", {"Text": {"text": "Second Tab Content"}}),
              (
                  "root",
                  {
                      "Tabs": {
                          "tabs": [
                              {"title": "View One", "child": "tab-1-content"},
                              {"title": "View Two", "child": "tab-2-content"},
                          ]
                      }
                  },
              ),
          ],
      },
  )

  # 9. Icon
  add_demo_surface(
      "demo-icon",
      {
          "0.8": [
              (
                  "root",
                  {
                      "Row": {
                          "children": {"explicitList": ["icon-1", "icon-2", "icon-3"]},
                          "distribution": "spaceEvenly",
                          "alignment": "center",
                      }
                  },
              ),
              ("icon-1", {"Icon": {"name": {"literalString": "star"}}}),
              ("icon-2", {"Icon": {"name": {"literalString": "home"}}}),
              ("icon-3", {"Icon": {"name": {"literalString": "settings"}}}),
          ],
          "0.9": [
              (
                  "root",
                  {
                      "Row": {
                          "children": ["icon-1", "icon-2", "icon-3"],
                          "justify": "spaceEvenly",
                          "align": "center",
                      }
                  },
              ),
              ("icon-1", {"Icon": {"name": "star"}}),
              ("icon-2", {"Icon": {"name": "home"}}),
              ("icon-3", {"Icon": {"name": "settings"}}),
          ],
      },
  )

  # 10. Divider
  add_demo_surface(
      "demo-divider",
      {
          "0.8": [
              (
                  "root",
                  {
                      "Column": {
                          "children": {"explicitList": ["div-text-1", "div-horiz", "div-text-2"]},
                          "distribution": "start",
                          "alignment": "stretch",
                      }
                  },
              ),
              ("div-text-1", {"Text": {"text": {"literalString": "Above Divider"}}}),
              ("div-horiz", {"Divider": {"axis": "horizontal"}}),
              ("div-text-2", {"Text": {"text": {"literalString": "Below Divider"}}}),
          ],
          "0.9": [
              (
                  "root",
                  {
                      "Column": {
                          "children": ["div-text-1", "div-horiz", "div-text-2"],
                          "justify": "start",
                          "align": "stretch",
                      }
                  },
              ),
              ("div-text-1", {"Text": {"text": "Above Divider"}}),
              ("div-horiz", {"Divider": {"axis": "horizontal"}}),
              ("div-text-2", {"Text": {"text": "Below Divider"}}),
          ],
      },
  )

  # 11. Card
  add_demo_surface(
      "demo-card",
      {
          "0.8": [
              ("root", {"Card": {"child": "card-text"}}),
              ("card-text", {"Text": {"text": {"literalString": "I am inside a Card"}}}),
          ],
          "0.9": [
              ("root", {"Card": {"child": "card-text"}}),
              ("card-text", {"Text": {"text": "I am inside a Card"}}),
          ],
      },
  )

  # 12. Video
  add_demo_surface(
      "demo-video",
      {
          "0.8": {
              "Video": {
                  # Still external as user only provided audio and image
                  "url": {
                      "literalString": (
                          "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
                      )
                  },
              }
          },
          "0.9": {
              "Video": {
                  "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
              }
          },
      },
  )

  # 13. Modal
  add_demo_surface(
      "demo-modal",
      {
          "0.8": [
              (
                  "root",
                  {
                      "Modal": {
                          "entryPointChild": "modal-btn",
                          "contentChild": "modal-content",
                      }
                  },
              ),
              (
                  "modal-btn",
                  {
                      "Button": {
                          "child": "modal-btn-text",
                          "primary": False,
                          "action": {"name": "noop"},
                      }
                  },
              ),
              ("modal-btn-text", {"Text": {"text": {"literalString": "Open Modal"}}}),
              (
                  "modal-content",
                  {"Text": {"text": {"literalString": "This is the modal content!"}}},
              ),
          ],
          "0.9": [
              (
                  "root",
                  {
                      "Modal": {
                          "trigger": "modal-btn",
                          "content": "modal-content",
                      }
                  },
              ),
              (
                  "modal-btn",
                  {
                      "Button": {
                          "child": "modal-btn-text",
                          "variant": "default",
                          "action": {
                              "event": {
                                  "name": "noop"
                              }
                          },
                      }
                  },
              ),
              ("modal-btn-text", {"Text": {"text": "Open Modal"}}),
              (
                  "modal-content",
                  {"Text": {"text": "This is the modal content!"}},
              ),
          ],
      },
  )

  # 14. List
  add_demo_surface(
      "demo-list",
      {
          "0.8": [
              (
                  "root",
                  {
                      "List": {
                          "children": {
                              "explicitList": [
                                  "list-item-1",
                                  "list-item-2",
                                  "list-item-3",
                              ]
                          },
                          "direction": "vertical",
                          "alignment": "stretch",
                      }
                  },
              ),
              ("list-item-1", {"Text": {"text": {"literalString": "Item 1"}}}),
              ("list-item-2", {"Text": {"text": {"literalString": "Item 2"}}}),
              ("list-item-3", {"Text": {"text": {"literalString": "Item 3"}}}),
          ],
          "0.9": [
              (
                  "root",
                  {
                      "List": {
                          "children": [
                              "list-item-1",
                              "list-item-2",
                              "list-item-3",
                          ],
                          "direction": "vertical",
                          "align": "stretch",
                      }
                  },
              ),
              ("list-item-1", {"Text": {"text": "Item 1"}}),
              ("list-item-2", {"Text": {"text": "Item 2"}}),
              ("list-item-3", {"Text": {"text": "Item 3"}}),
          ],
      },
  )

  # 15. AudioPlayer
  add_demo_surface(
      "demo-audio",
      {
          "0.8": {
              "AudioPlayer": {
                  "url": {"literalString": "http://localhost:10005/assets/audio.mp3"},
                  "description": {"literalString": "Local Audio Sample"},
              }
          },
          "0.9": {
              "AudioPlayer": {
                  "url": "http://localhost:10005/assets/audio.mp3",
                  "description": "Local Audio Sample",
              }
          },
      },
  )

  # Response Surface
  if version == "0.8":
    messages.append(
        {"beginRendering": {"surfaceId": "response-surface", "root": "response-text"}}
    )
    messages.append({
        "surfaceUpdate": {
            "surfaceId": "response-surface",
            "components": [
                wrap_component(
                    "response-text",
                    {
                        "Text": {
                            "text": {
                                "literalString": (
                                    "Interact with the gallery to see responses. This view is"
                                    " updated by the agent by relaying the raw action"
                                    " commands it received from the client"
                                )
                            }
                        }
                    },
                ),
            ],
        }
    })
  else:
    messages.append({
        "version": "v0.9",
        "createSurface": {
            "surfaceId": "response-surface",
            "catalogId": "https://a2ui.org/specification/v0_9/basic_catalog.json",
        },
    })
    messages.append({
        "version": "v0.9",
        "updateComponents": {
            "surfaceId": "response-surface",
            "components": [
                wrap_component(
                    "root",
                    {
                        "Text": {
                            "text": (
                                "Interact with the gallery to see responses. This view is"
                                " updated by the agent by relaying the raw action"
                                " commands it received from the client"
                            )
                        }
                    },
                ),
            ],
        },
    })

  return json.dumps(messages, indent=2)
