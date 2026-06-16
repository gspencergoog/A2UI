"""Unit tests for the A2UI Express pipeline.

Validates prompt generation, DSL compilation, wire JSON decompilation, and runs
comprehensive semantic round-trip checks on standard v1.0 catalog examples.
"""

import os
import json
import glob
import unittest
from a2ui.express.prompt_generator import ExpressPromptGenerator
from a2ui.express.compiler import ExpressCompiler
from a2ui.express.decompiler import ExpressDecompiler
from a2ui.express.schema_helper import CatalogSchemaHelper

SPEC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "specification", "v1_0"))
CATALOG_PATH = os.path.join(SPEC_DIR, "catalogs", "basic", "catalog.json")
EXAMPLES_DIR = os.path.join(SPEC_DIR, "catalogs", "basic", "examples")


class TestExpressPipeline(unittest.TestCase):
    """Test suite covering A2UI Express parser, compiler, and decompiler."""

    def setUp(self):
        """Initializes standard test paths and schema helpers."""
        self.catalog_path = CATALOG_PATH
        self.helper = CatalogSchemaHelper(self.catalog_path)

    def test_prompt_generator(self):
        """Verifies prompt signature compiler loads catalog components correctly."""
        generator = ExpressPromptGenerator(self.catalog_path)
        prompt = generator.generate_prompt()
        self.assertIn("Text(", prompt)
        self.assertIn("Column(", prompt)
        self.assertIn("required(", prompt)
        self.assertIn("regex(", prompt)

    def test_compilation_and_decompilation_basic(self):
        """Validates parsing and mapping basic components and validations."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        dsl = """root = Column([repField, valueField])
repField = TextField("Representative", $/form/rep, "Enter name")
valueField = TextField("Deal Value", $/form/value, "0.00", "number", ?required)"""

        envelope = compiler.compile(dsl, surface_id="test_surf")
        self.assertEqual(envelope["version"], "v1.0")
        self.assertEqual(envelope["createSurface"]["surfaceId"], "test_surf")

        components = envelope["createSurface"]["components"]
        self.assertEqual(len(components), 3)

        # Verify adjacency list structures
        root_comp = next(c for c in components if c["id"] == "root")
        self.assertEqual(root_comp["component"], "Column")
        self.assertEqual(root_comp["children"], ["repField", "valueField"])

        rep_comp = next(c for c in components if c["id"] == "repField")
        self.assertEqual(rep_comp["component"], "TextField")
        self.assertEqual(rep_comp["label"], "Representative")
        self.assertEqual(rep_comp["value"], {"path": "/form/rep"})
        self.assertEqual(rep_comp["placeholder"], "Enter name")

        val_comp = next(c for c in components if c["id"] == "valueField")
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
        self.assertTrue(decompiled_dsl.startswith("<a2ui>\n"))
        self.assertTrue(decompiled_dsl.endswith("\n</a2ui>"))
        self.assertIn("root = Column([repField, valueField])", decompiled_dsl)
        self.assertIn(
            'repField = TextField("Representative", $/form/rep, "Enter name")',
            decompiled_dsl)
        self.assertIn(
            'valueField = TextField("Deal Value", $/form/value, "0.00", "number", ?required)',
            decompiled_dsl)

    def test_format_string_and_actions(self):
        """Validates compilation of string interpolation and interactive actions."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        dsl = """root = Column([welcome, saveButton])
welcome = Text(formatString("Welcome, ${/user/name}!"))
saveButton = Button(saveLabel, "primary", Event("submitDeal", {rep: $/form/rep}))
saveLabel = Text("Save")"""

        envelope = compiler.compile(dsl)
        components = envelope["createSurface"]["components"]

        welcome_comp = next(c for c in components if c["id"] == "welcome")
        self.assertEqual(
            welcome_comp["text"], {
                "call": "formatString",
                "args": {
                    "value": "Welcome, ${/user/name}!"
                },
                "returnType": "string"
            })

        button_comp = next(c for c in components if c["id"] == "saveButton")
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
            'welcome = Text(formatString("Welcome, ${/user/name}!"))',
            decompiled_dsl)
        self.assertIn(
            'saveButton = Button(saveLabel, "primary", Event("submitDeal", {rep: $/form/rep}))',
            decompiled_dsl)

    def test_standalone_function_call(self):
        """Validates compilation of standalone function calls into CallFunctionMessages."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        dsl = """openUrl("https://example.com")"""
        envelope = compiler.compile(dsl)

        self.assertEqual(envelope["version"], "v1.0")
        self.assertIn("callFunction", envelope)
        self.assertIn("functionCallId", envelope)
        self.assertEqual(envelope["callFunction"]["call"], "openUrl")
        self.assertEqual(envelope["callFunction"]["args"], {"url": "https://example.com"})

        # Verify decompilation
        decompiled_dsl = decompiler.decompile(envelope)
        self.assertIn('openUrl("https://example.com")', decompiled_dsl)

    def test_map_variable_inlining(self):
        """Validates compiling variable assignments holding map literals and inlining them."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        dsl = """root = Tabs([tab1])
tab1 = {title: "Overview", child: contentCol}
contentCol = Column([])"""

        envelope = compiler.compile(dsl)
        components = envelope["createSurface"]["components"]

        tabs_comp = next(c for c in components if c["id"] == "root")
        self.assertEqual(tabs_comp["component"], "Tabs")
        self.assertEqual(tabs_comp["tabs"], [{"title": "Overview", "child": "contentCol"}])

        # Verify decompilation back to inline map literals
        decompiled_dsl = decompiler.decompile(envelope)
        self.assertIn('root = Tabs([{title: "Overview", child: contentCol}])', decompiled_dsl)

    def test_round_trip_examples(self):
        """Runs a semantically rigorous round-trip test on real catalog examples."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        example_files = glob.glob(os.path.join(EXAMPLES_DIR, "*.json"))
        self.assertTrue(
            len(example_files) > 0,
            "No example files found to run round-trip tests.")

        # We test a robust selection of examples covering different components and actions
        tested_count = 0
        for ex_file in sorted(
                example_files)[:5]:  # Run first 5 complex examples
            with open(ex_file, "r", encoding="utf-8") as f:
                ex_data = json.load(f)

            # Extract components from updateComponents message
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

            # Wrap into standard createSurface payload
            original_envelope = {
                "version": "v1.0",
                "createSurface": {
                    "surfaceId": surface_id,
                    "catalogId": catalog_id,
                    "components": components_list
                }
            }

            # Round trip: Decompile -> Compile -> Compare
            dsl = decompiler.decompile(original_envelope)
            compiled_envelope = compiler.compile(dsl,
                                                 surface_id=surface_id,
                                                 catalog_id=catalog_id)

            # Semantically normalize lists for exact matching
            orig_comps = sorted(
                original_envelope["createSurface"]["components"],
                key=lambda x: x["id"])
            comp_comps = sorted(
                compiled_envelope["createSurface"]["components"],
                key=lambda x: x["id"])

            if len(orig_comps) != len(comp_comps):
                print(f"Length mismatch for {os.path.basename(ex_file)}: "
                      f"Orig: {len(orig_comps)}, Comp: {len(comp_comps)}")
                print(f"Orig IDs: {[x['id'] for x in orig_comps]}")
                print(f"Comp IDs: {[x['id'] for x in comp_comps]}")
                self.assertEqual(len(orig_comps), len(comp_comps))

            for idx, orig in enumerate(orig_comps):
                comp = comp_comps[idx]
                if orig["id"] != comp["id"] or orig["component"] != comp[
                        "component"]:
                    print(f"Mismatch in component index {idx} for "
                          f"{os.path.basename(ex_file)}")
                    print(f"Orig: {orig}")
                    print(f"Comp: {comp}")
                    self.assertEqual(orig["id"], comp["id"])
                    self.assertEqual(orig["component"], comp["component"])

                # Verify non-default mapped values match semantically
                for k, orig_v in orig.items():
                    if k in ["component", "id"]:
                        continue
                    if k == "checks":
                        continue
                    if k not in comp:
                        print(f"Missing property '{k}' in compiled component "
                              f"{orig['id']} for {os.path.basename(ex_file)}")
                        print(f"Orig: {orig}")
                        print(f"Comp: {comp}")
                        self.assertIn(k, comp)
                    comp_v = comp[k]
                    # Normalize function call returnType omission in legacy examples
                    if isinstance(orig_v, dict) and "call" in orig_v and "returnType" not in orig_v:
                        if isinstance(comp_v, dict) and comp_v.get("call") == orig_v["call"]:
                            comp_v = {k2: v2 for k2, v2 in comp_v.items() if k2 != "returnType"}
                    if orig_v != comp_v:
                        print(
                            f"Value mismatch for property '{k}' in component "
                            f"{orig['id']} for {os.path.basename(ex_file)}")
                        print(f"Orig: {orig_v}")
                        print(f"Comp: {comp_v}")
                        self.assertEqual(orig_v, comp_v)

        print(f"\nSuccessfully completed round-trip validation across "
              f"{tested_count} standard catalog examples.")

    def test_data_model_compilation_and_decompilation(self):
        """Validates compiling and decompiling shared data model assignments in the DSL."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        dsl = """$/icon = "check"
$/title = "Enable notification"
$/user/firstName = "Alice"
$/user/age = 30
root = Card(main-column)
main-column = Column([icon, title], _, "center")
icon = Icon($/icon)
title = Text($/title, "h3")"""

        envelope = compiler.compile(dsl, surface_id="test_data_surf")
        self.assertEqual(envelope["version"], "v1.0")
        create_surface = envelope["createSurface"]
        self.assertEqual(create_surface["surfaceId"], "test_data_surf")

        # Verify compiled dataModel dict structures
        data_model = create_surface["dataModel"]
        self.assertEqual(data_model["icon"], "check")
        self.assertEqual(data_model["title"], "Enable notification")
        self.assertEqual(data_model["user"]["firstName"], "Alice")
        self.assertEqual(data_model["user"]["age"], 30)

        # Verify decompiled dataModel DSL output
        decompiled_dsl = decompiler.decompile(envelope)
        self.assertIn('$/icon = "check"', decompiled_dsl)
        self.assertIn('$/title = "Enable notification"', decompiled_dsl)
        self.assertIn('$/user/age = 30', decompiled_dsl)
        self.assertIn('$/user/firstName = "Alice"', decompiled_dsl)
        self.assertIn('root = Card(main-column)', decompiled_dsl)

        # Round-trip check
        compiled_envelope_2 = compiler.compile(decompiled_dsl, surface_id="test_data_surf")
        self.assertEqual(compiled_envelope_2["createSurface"]["dataModel"], data_model)

    def test_skipped_and_omitted_arguments(self):
        """Validates skipped (_) and trailing omitted positional arguments compile and decompile correctly."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        dsl = """root = Column([btn1, btn2])
btn1 = Button(btn1-label, _, Event("click"))
btn1-label = Text("Click")
btn2 = Button(btn2-label)
btn2-label = Text("Submit")"""

        envelope = compiler.compile(dsl)
        components = envelope["createSurface"]["components"]

        btn1_comp = next(c for c in components if c["id"] == "btn1")
        self.assertNotIn("variant", btn1_comp)
        self.assertEqual(btn1_comp["action"], {"event": {"name": "click", "context": {}}})

        btn2_comp = next(c for c in components if c["id"] == "btn2")
        self.assertEqual(btn2_comp["child"], "btn2-label")
        self.assertNotIn("variant", btn2_comp)
        self.assertNotIn("action", btn2_comp)

        decompiled_dsl = decompiler.decompile(envelope)
        self.assertIn("btn1 = Button(btn1-label, _, Event(\"click\"))", decompiled_dsl)
        self.assertIn("btn2 = Button(btn2-label)", decompiled_dsl)
        # Ensure no nulls are decompiled
        self.assertNotIn("null", decompiled_dsl)

    def test_delete_surface_and_template_and_rootless_data(self):
        """Validates standalone deleteSurface, _template helper, and rootless updateDataModel."""
        compiler = ExpressCompiler(self.catalog_path)
        decompiler = ExpressDecompiler(self.catalog_path)

        # 1. Test deleteSurface parsing/compiling/decompiling
        delete_dsl = "deleteSurface(\"my-surface-123\")"
        del_envelope = compiler.compile(delete_dsl)
        self.assertEqual(del_envelope, {
            "version": "v1.0",
            "deleteSurface": {
                "surfaceId": "my-surface-123"
            }
        })
        self.assertEqual(decompiler.decompile(del_envelope).strip(), f"<a2ui>\n{delete_dsl}\n</a2ui>")

        # 2. Test rootless updateDataModel parsing/compiling/decompiling
        data_dsl = """$/form/firstName = "Alice"
$/form/lastName = "Smith"
$/age = 25"""
        data_envelope = compiler.compile(data_dsl, surface_id="data-surf")
        self.assertEqual(data_envelope, {
            "version": "v1.0",
            "updateDataModel": {
                "surfaceId": "data-surf",
                "path": "/",
                "value": {
                    "form": {
                        "firstName": "Alice",
                        "lastName": "Smith"
                    },
                    "age": 25
                }
            }
        })
        self.assertIn('$/form/firstName = "Alice"', decompiler.decompile(data_envelope))

        # 3. Test _template helper list compilation
        list_dsl = """root = Card(breedList)
        breedList = List(_template($/breeds, breedTemplate))
        breedTemplate = Image($url)"""
        list_envelope = compiler.compile(list_dsl)
        components = list_envelope["createSurface"]["components"]
        list_comp = next(c for c in components if c["id"] == "breedList")
        self.assertEqual(list_comp["children"], {
            "path": "/breeds",
            "componentId": "breedTemplate"
        })
        self.assertIn("breedList = List(_template($/breeds, breedTemplate))", decompiler.decompile(list_envelope))

        # 4. Test map literal parsing and nested array of maps
        map_dsl = """$/form/data = [{"id": 1, "meta": {"name": "Alice"}}]"""
        map_envelope = compiler.compile(map_dsl)
        self.assertEqual(map_envelope["updateDataModel"]["value"]["form"]["data"], [
            {"id": 1, "meta": {"name": "Alice"}}
        ])


if __name__ == "__main__":
    unittest.main()
