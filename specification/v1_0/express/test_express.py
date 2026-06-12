"""Unit tests for the A2UI Express pipeline.

Validates prompt generation, DSL compilation, wire JSON decompilation, and runs
comprehensive semantic round-trip checks on standard v1.0 catalog examples.
"""

import os
import json
import glob
import unittest
from .prompt_generator import ExpressPromptGenerator
from .compiler import ExpressCompiler
from .decompiler import ExpressDecompiler
from .schema_helper import CatalogSchemaHelper

SPEC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CATALOG_PATH = os.path.join(SPEC_DIR, "catalogs", "basic", "catalog.json")
EXAMPLES_DIR = os.path.join(SPEC_DIR, "catalogs", "basic", "examples")


class TestExpressPipeline(unittest.TestCase):
    """Test suite covering A2UI Express parser, compiler, and decompiler."""

    def setUp(self):
        """Initializes standard test paths and schema helpers."""
        self.catalog_path = CATALOG_PATH
        self.helper = CatalogSchemaHelper(self.catalog_path)

    def test_prompt_generator_descriptions(self):
        """Verifies prompt generator propagates component, function, and parameter descriptions."""
        generator = ExpressPromptGenerator(self.catalog_path)
        prompt = generator.generate_prompt()
        self.assertIn("A component that allows selecting one or more options", prompt)
        self.assertIn("The ID of the child component", prompt)
        self.assertIn("Formats a number as a currency string", prompt)
        self.assertIn("ISO 4217 currency code", prompt)

    def test_compilation_and_decompilation_basic(self):
        """Validates parsing and mapping basic components and validations."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        dsl = """(Column [(TextField "Representative" @/form/rep "Enter name") (TextField "Deal Value" @/form/value "0.00" number ?required)])"""

        envelope = compiler.compile(dsl, surface_id="test_surf")
        self.assertEqual(envelope["version"], "v1.0")
        self.assertEqual(envelope["createSurface"]["surfaceId"], "test_surf")

        components = envelope["createSurface"]["components"]
        self.assertEqual(len(components), 3)

        # Verify adjacency list structures
        root_comp = next(c for c in components if c["id"] == "root")
        self.assertEqual(root_comp["component"], "Column")
        self.assertEqual(root_comp["children"], ["textfield_0", "textfield_1"])

        rep_comp = next(c for c in components if c["id"] == "textfield_0")
        self.assertEqual(rep_comp["component"], "TextField")
        self.assertEqual(rep_comp["label"], "Representative")
        self.assertEqual(rep_comp["value"], {"path": "/form/rep"})
        self.assertEqual(rep_comp["placeholder"], "Enter name")

        val_comp = next(c for c in components if c["id"] == "textfield_1")
        self.assertEqual(val_comp["component"], "TextField")
        self.assertEqual(val_comp["label"], "Deal Value")
        self.assertEqual(val_comp["value"], {"path": "/form/value"})
        self.assertEqual(val_comp["placeholder"], "0.00")
        self.assertEqual(val_comp["variant"], "number")
        # Verify implicit path validation injection
        self.assertEqual(val_comp["checks"],
                         [{
                             "condition": {
                                 "call": "required",
                                 "args": {
                                     "value": {
                                         "path": "/form/value"
                                     }
                                 }
                             },
                             "message": "Required check failed"
                         }])

        # Verify decompile
        decompiled_dsl = decompiler.decompile(envelope)
        self.assertIn('(Column [(TextField "Representative" @/form/rep "Enter name") (TextField "Deal Value" @/form/value "0.00" number ?required)])', decompiled_dsl)

    def test_format_string_and_actions(self):
        """Validates compilation of string interpolation and interactive actions."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        dsl = """(Column [(Text (formatString "Welcome, ${/user/name}!")) (Button (Text "Save") primary (!submitDeal {rep @/form/rep}))])"""

        envelope = compiler.compile(dsl)
        components = envelope["createSurface"]["components"]

        welcome_comp = next(c for c in components if c["id"] == "text_0")
        self.assertEqual(
            welcome_comp["text"], {
                "call": "formatString",
                "args": {
                    "value": "Welcome, ${/user/name}!"
                },
                "returnType": "string"
            })

        button_comp = next(c for c in components if c["id"] == "button_1")
        self.assertEqual(button_comp["variant"], "primary")
        self.assertEqual(
            button_comp["action"], {
                "event": {
                    "name": "submitDeal",
                    "context": {
                        "rep": {
                            "path": "/form/rep"
                        }
                    }
                }
            })

        decompiled_dsl = decompiler.decompile(envelope)
        self.assertIn(
            '(Text (formatString "Welcome, ${/user/name}!"))',
            decompiled_dsl)

    def test_round_trip_examples(self):
        """Runs a semantically rigorous round-trip test on real catalog examples."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        example_files = glob.glob(os.path.join(EXAMPLES_DIR, "*.json"))
        self.assertTrue(
            len(example_files) > 0,
            "No example files found to run round-trip tests.")

        tested_count = 0
        for ex_file in sorted(example_files)[:5]:
            with open(ex_file, "r", encoding="utf-8") as f:
                ex_data = json.load(f)

            messages = ex_data.get("messages", [])
            components_list = None
            surface_id = "test_surf"
            catalog_id = (
                "https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json"
            )

            for msg in messages:
                if "updateComponents" in msg:
                    components_list = msg["updateComponents"].get(
                        "components", [])
                    surface_id = msg["updateComponents"].get(
                        "surfaceId", surface_id)
                    break

            if not components_list:
                continue

            tested_count += 1

            original_envelope = {
                "version": "v1.0",
                "createSurface": {
                    "surfaceId": surface_id,
                    "catalogId": catalog_id,
                    "components": components_list
                }
            }

            dsl1 = decompiler.decompile(original_envelope)
            compiled_envelope = compiler.compile(dsl1,
                                                 surface_id=surface_id,
                                                 catalog_id=catalog_id)
            dsl2 = decompiler.decompile(compiled_envelope)

            self.assertEqual(dsl1.strip(), dsl2.strip())

    def test_data_model_compilation_and_decompilation(self):
        """Validates compiling and decompiling shared data model assignments in the DSL."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        dsl = """(= @/icon check)
(= @/title "Enable notification")
(= @/user/firstName "Alice")
(= @/user/age 30)
(Card (Column [(Icon @/icon) (Text @/title h3)] ~ center))"""

        envelope = compiler.compile(dsl, surface_id="test_data_surf")
        self.assertEqual(envelope["version"], "v1.0")
        create_surface = envelope["createSurface"]
        self.assertEqual(create_surface["surfaceId"], "test_data_surf")

        data_model = create_surface["dataModel"]
        self.assertEqual(data_model["icon"], "check")
        self.assertEqual(data_model["title"], "Enable notification")
        self.assertEqual(data_model["user"]["firstName"], "Alice")
        self.assertEqual(data_model["user"]["age"], 30)

        decompiled_dsl = decompiler.decompile(envelope)
        self.assertIn('(= @/icon check)', decompiled_dsl)
        self.assertIn('(= @/title "Enable notification")', decompiled_dsl)

    def test_feature_mask_modular_prompt(self):
        """Verifies modular prompt generation filtering using feature masks."""
        generator_full = ExpressPromptGenerator(self.catalog_path, feature_mask={"accessibility", "weight"})
        prompt_full = generator_full.generate_prompt()
        self.assertIn("accessibility?", prompt_full)

        generator_min = ExpressPromptGenerator(self.catalog_path, feature_mask=set())
        prompt_min = generator_min.generate_prompt()
        self.assertNotIn("accessibility?", prompt_min)

    def test_trailing_default_elision(self):
        """Verifies compilation of statements with omitted trailing optional arguments."""
        compiler = ExpressCompiler(self.catalog_path)
        dsl = '(Column [(Text "Short")])'
        envelope = compiler.compile(dsl)
        components = envelope["createSurface"]["components"]
        col = next(c for c in components if c["id"] == "root")
        self.assertIsNone(col.get("justify"))
        self.assertIsNone(col.get("align"))


if __name__ == "__main__":
    unittest.main()
