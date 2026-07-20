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

"""Unit tests for A2UI Atom inference format compiler and decompiler."""

import unittest
from typing import Any, Dict
from a2ui.inference_formats.experimental.atom.compiler import AtomCompiler
from a2ui.inference_formats.experimental.atom.decompiler import AtomDecompiler


class MockCatalog:
    def __init__(self):
        self.id = "basic"

    def get_components(self):
        return {
            "Card": {"properties": {"child": {"type": "string"}, "children": {"type": "array"}}},
            "Column": {"properties": {"children": {"type": "array"}, "align": {"type": "string"}}},
            "Row": {"properties": {"children": {"type": "array"}, "justify": {"type": "string"}, "align": {"type": "string"}}},
            "Text": {"properties": {"text": {"type": "string"}, "variant": {"type": "string"}}},
            "Icon": {"properties": {"name": {"type": "string"}}},
            "Button": {"properties": {"child": {"type": "string"}, "action": {"type": "object"}}},
        }


class TestAtomFormat(unittest.TestCase):

    def setUp(self):
        self.catalog = MockCatalog()
        self.compiler = AtomCompiler(self.catalog)
        self.decompiler = AtomDecompiler(self.catalog)

    def test_compile_notification_card(self):
        text = """(data $/icon "check" $/title "Enable notification")
(Card
  (Column :align "center"
    (Icon $/icon)
    (Text $/title)
    (Row :justify "center"
      (Button :action (Event "accept") (Text "Yes")))))"""
        
        compiled = self.compiler.compile(text)
        self.assertIn("createSurface", compiled)
        surface = compiled["createSurface"]
        self.assertEqual(surface["dataModel"]["icon"], "check")
        self.assertEqual(surface["dataModel"]["title"], "Enable notification")
        
        comps = surface["components"]
        self.assertGreater(len(comps), 0)
        self.assertEqual(comps[0]["component"], "Card")

    def test_compile_auto_healing_missing_parens(self):
        # Truncated S-expression missing trailing parens at EOF
        text = """(Card (Column (Text "Hello World"""
        compiled = self.compiler.compile(text)
        self.assertIn("createSurface", compiled)
        comps = compiled["createSurface"]["components"]
        self.assertGreater(len(comps), 0)
        self.assertEqual(comps[0]["component"], "Card")

    def test_compile_delete_surface(self):
        text = '(deleteSurface "dashboard-1")'
        compiled = self.compiler.compile(text)
        self.assertIn("deleteSurface", compiled)
        self.assertEqual(compiled["deleteSurface"]["surfaceId"], "dashboard-1")

    def test_compile_call_function(self):
        text = '(callFunction "openUrl" :url "https://example.com")'
        compiled = self.compiler.compile(text)
        self.assertIn("callFunction", compiled)
        self.assertEqual(compiled["callFunction"]["call"], "openUrl")
        self.assertEqual(compiled["callFunction"]["args"]["url"], "https://example.com")

    def test_decompile_round_trip(self):
        original = {
            "version": "v1.0",
            "createSurface": {
                "surfaceId": "main",
                "catalogId": "basic",
                "dataModel": {"title": "Welcome"},
                "components": [
                    {"id": "node_0", "component": "Card", "child": "node_1"},
                    {"id": "node_1", "component": "Text", "text": "Hello"}
                ]
            }
        }
        decompiled_text = self.decompiler.decompile(original)
        self.assertIn('(data $/title "Welcome")', decompiled_text)
        self.assertIn('(Card', decompiled_text)
        self.assertIn('(Text :text "Hello")', decompiled_text)

    def test_regression_data_model_brackets_and_empty_arrays(self):
        """Regression test: (data $/rating [] $/likes [] $/comments "") must compile empty arrays cleanly."""
        text_data_only = '(data $/rating [] $/likes [] $/comments "")'
        compiled_data = self.compiler.compile(text_data_only)
        self.assertIn("updateDataModel", compiled_data)
        self.assertEqual(
            compiled_data["updateDataModel"]["value"],
            {"rating": [], "likes": [], "comments": ""}
        )

        text_with_card = '(data $/rating [] $/likes [] $/comments "") (Card (Text "Hello"))'
        compiled_surface = self.compiler.compile(text_with_card)
        self.assertIn("createSurface", compiled_surface)
        self.assertEqual(
            compiled_surface["createSurface"]["dataModel"],
            {"rating": [], "likes": [], "comments": ""}
        )

    def test_regression_action_event_object_structure(self):
        """Regression test: Button action events must emit action: {"event": {"name": "event_name", "context": {...}}}."""
        text = '(Card (Button :action (Event "generate_dog" :name $/gen/name) (Text "Submit")))'
        compiled = self.compiler.compile(text)
        comps = compiled["createSurface"]["components"]
        btn = next(c for c in comps if c["component"] == "Button")
        self.assertEqual(
            btn["action"],
            {"event": {"name": "generate_dog", "context": {"name": {"path": "/gen/name"}}}}
        )

    def test_regression_unwrap_create_surface_macro_expression(self):
        """Regression test: Outer (createSurface "main" ...) macro forms must not create invalid component nodes."""
        text = '(createSurface "main" (Column (Text "Hello World")))'
        compiled = self.compiler.compile(text)
        comps = compiled["createSurface"]["components"]
        comp_types = [c["component"] for c in comps]
        self.assertNotIn("createSurface", comp_types)
        self.assertIn("Column", comp_types)
        self.assertIn("Text", comp_types)


if __name__ == "__main__":
    unittest.main()
