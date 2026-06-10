"""Unit tests verifying ExpressMutator XML extraction and AST self-repair."""

import os
import unittest
from unittest.mock import MagicMock, patch
from ..manifest import Gene
from ..mutator import ExpressMutator

SPEC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class TestExpressMutator(unittest.TestCase):
    """Test suite covering XML tag extraction and automated syntax retry loops."""

    def setUp(self):
        """Initializes standard paths and dummy champion genes."""
        self.prompt_path = os.path.join(SPEC_DIR, "optimizer", "mutate_prompt.md")
        self.champion = Gene(
            gene_id="gene_v1_0",
            a2ui_express_content="# Spec",
            basic_prompt_content="Prompt",
            compiler_content="x = 1",
            decompiler_content="y = 2",
        )

    def test_extract_xml_block_clean(self):
        """Verifies robust regex extraction across multiline XML structures."""
        mutator = ExpressMutator(self.prompt_path)
        sample = "<compiler.py>\ndef parse():\n    pass\n</compiler.py>"
        extracted = mutator._extract_xml_block(sample, "compiler.py")
        self.assertEqual(extracted, "def parse():\n    pass")

    def test_generate_mutation_ast_self_repair(self):
        """Verifies mutator catches SyntaxError and successfully self-repairs on retry."""
        mock_client = MagicMock()

        # Attempt 1: Output contains invalid Python syntax in compiler.py
        bad_response = MagicMock()
        bad_response.text = (
            "<a2ui_express.md># Mutated</a2ui_express.md>\n"
            "<basic_prompt.md>Mutated Prompt</basic_prompt.md>\n"
            "<compiler.py>def unclosed_paren(: pass</compiler.py>\n"
            "<decompiler.py>def clean(): pass</decompiler.py>"
        )

        # Attempt 2: Model self-corrects and outputs valid Python AST
        good_response = MagicMock()
        good_response.text = (
            "<a2ui_express.md># Mutated</a2ui_express.md>\n"
            "<basic_prompt.md>Mutated Prompt</basic_prompt.md>\n"
            "<compiler.py>def closed_paren(): pass</compiler.py>\n"
            "<decompiler.py>def clean(): pass</decompiler.py>"
        )

        mock_client.models.generate_content.side_effect = [bad_response, good_response]

        mutator = ExpressMutator(self.prompt_path)
        mutator.client = mock_client

        offspring = mutator.generate_mutation(self.champion, max_retries=2)
        self.assertIsNotNone(offspring)
        self.assertEqual(offspring.parent_id, "gene_v1_0")
        self.assertEqual(offspring.compiler_content, "def closed_paren(): pass")
        self.assertEqual(mock_client.models.generate_content.call_count, 2)


if __name__ == "__main__":
    unittest.main()
