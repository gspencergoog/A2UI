"""Unit tests verifying candidate gene serialization and hashing."""

import dataclasses
import os
import shutil
import tempfile
import unittest
from ..manifest import Gene


class TestGeneManifest(unittest.TestCase):
    """Verifies Gene SHA-256 hashing and bidirectional disk packaging."""

    def setUp(self):
        """Creates a temporary sandbox directory for disk tests."""
        self.test_dir = tempfile.mkdtemp()
        self.gene = Gene(
            gene_id="gene_test",
            a2ui_express_content="# Test Spec",
            basic_prompt_content="You are an agent",
            compiler_content="print('compile')",
            decompiler_content="print('decompile')",
            parent_id="gene_v1_0",
            fitness_score=0.95,
            metrics={"compression": 0.5},
        )

    def tearDown(self):
        """Cleans up temporary disk artifacts."""
        shutil.rmtree(self.test_dir)

    def test_compute_hash_deterministic(self):
        """Verifies identical genetic content produces identical SHA-256 hashes."""
        h1 = self.gene.compute_hash()
        h2 = self.gene.compute_hash()
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 12)

        # Mutating content alters hash
        mutated = dataclasses.replace(self.gene, compiler_content="pass")
        self.assertNotEqual(h1, mutated.compute_hash())

    def test_save_and_load_roundtrip(self):
        """Verifies saving and loading reconstructs exact artifacts and metadata."""
        self.gene.save_to_disk(self.test_dir)

        loaded = Gene.load_from_disk(os.path.join(self.test_dir, "gene_test"))
        self.assertEqual(loaded.gene_id, self.gene.gene_id)
        self.assertEqual(loaded.a2ui_express_content, self.gene.a2ui_express_content)
        self.assertEqual(loaded.compiler_content, self.gene.compiler_content)
        self.assertEqual(loaded.fitness_score, self.gene.fitness_score)
        self.assertEqual(loaded.metrics, self.gene.metrics)


if __name__ == "__main__":
    unittest.main()
