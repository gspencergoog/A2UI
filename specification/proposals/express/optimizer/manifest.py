"""Candidate gene packaging and lineage serialization for A2UI Express optimizer.

Defines the Gene data model encapsulating specification prose, LLM prompts,
and Python parsing rules. Provides SHA-256 hashing and disk packaging.
"""

import dataclasses
import hashlib
import json
import os
from typing import Any, Optional


@dataclasses.dataclass
class Gene:
    """Represents a synchronized candidate mutation bundle."""
    gene_id: str
    a2ui_express_content: str
    basic_prompt_content: str
    compiler_content: str
    decompiler_content: str
    parent_id: Optional[str] = None
    fitness_score: float = 0.0
    metrics: dict[str, Any] = dataclasses.field(default_factory=dict)

    def compute_hash(self) -> str:
        """Computes a SHA-256 hash uniquely identifying this genetic content."""
        hasher = hashlib.sha256()
        hasher.update(self.a2ui_express_content.encode("utf-8"))
        hasher.update(self.basic_prompt_content.encode("utf-8"))
        hasher.update(self.compiler_content.encode("utf-8"))
        hasher.update(self.decompiler_content.encode("utf-8"))
        return hasher.hexdigest()[:12]

    def save_to_disk(self, target_dir: str) -> None:
        """Serializes the gene bundle and its four core artifacts to disk.

        Args:
            target_dir: The directory path where the gene folder will be created.
        """
        gene_dir = os.path.join(target_dir, self.gene_id)
        os.makedirs(gene_dir, exist_ok=True)

        with open(os.path.join(gene_dir, "a2ui_express.md"), "w", encoding="utf-8") as f:
            f.write(self.a2ui_express_content)
        with open(os.path.join(gene_dir, "basic_prompt.md"), "w", encoding="utf-8") as f:
            f.write(self.basic_prompt_content)
        with open(os.path.join(gene_dir, "compiler.py"), "w", encoding="utf-8") as f:
            f.write(self.compiler_content)
        with open(os.path.join(gene_dir, "decompiler.py"), "w", encoding="utf-8") as f:
            f.write(self.decompiler_content)

        metadata = {
            "gene_id": self.gene_id,
            "parent_id": self.parent_id,
            "content_hash": self.compute_hash(),
            "fitness_score": self.fitness_score,
            "metrics": self.metrics,
        }
        with open(os.path.join(gene_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    @classmethod
    def load_from_disk(cls, gene_dir: str) -> "Gene":
        """Deserializes a candidate gene bundle from disk.

        Args:
            gene_dir: Path to the specific gene folder containing artifacts.

        Returns:
            The reconstructed Gene instance.
        """
        with open(os.path.join(gene_dir, "a2ui_express.md"), "r", encoding="utf-8") as f:
            a2ui_express_content = f.read()
        with open(os.path.join(gene_dir, "basic_prompt.md"), "r", encoding="utf-8") as f:
            basic_prompt_content = f.read()
        with open(os.path.join(gene_dir, "compiler.py"), "r", encoding="utf-8") as f:
            compiler_content = f.read()
        with open(os.path.join(gene_dir, "decompiler.py"), "r", encoding="utf-8") as f:
            decompiler_content = f.read()

        metadata_path = os.path.join(gene_dir, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        else:
            meta = {}

        return cls(
            gene_id=meta.get("gene_id", os.path.basename(gene_dir)),
            a2ui_express_content=a2ui_express_content,
            basic_prompt_content=basic_prompt_content,
            compiler_content=compiler_content,
            decompiler_content=decompiler_content,
            parent_id=meta.get("parent_id"),
            fitness_score=meta.get("fitness_score", 0.0),
            metrics=meta.get("metrics", {}),
        )

    @classmethod
    def load_baseline(cls, spec_express_dir: str) -> "Gene":
        """Constructs the baseline gene_v1_0 from active specification files."""
        return cls.load_from_disk(spec_express_dir)
