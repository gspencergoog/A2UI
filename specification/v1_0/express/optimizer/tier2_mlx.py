"""Tier 2 local MLX micro-inference gating client for A2UI Express optimizer.

Queries a local background mlx_vlm server (http://localhost:8080) with a hard
30-token limit and 2-second timeout to instantly verify small-model comprehension.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Optional

# Support direct execution from worktree root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

# pylint: disable=import-error, wrong-import-position
from specification.v1_0.express.compiler import ExpressCompiler
# pylint: enable=import-error, wrong-import-position


class LocalMLXLinter:
    """Instantly evaluates small-model syntax comprehension via local MLX server."""

    def __init__(
        self,
        endpoint_url: str = "http://localhost:8080/v1/chat/completions",
        model_name: str = "mlx-community/gemma-4-e2b-it-4bit",
        timeout_seconds: float = 2.0,
        max_tokens: int = 30,
    ):
        """Initializes the linter with local socket configuration.

        Args:
            endpoint_url: HTTP URL to local OpenAI-compatible MLX server.
            model_name: Target small model identifier.
            timeout_seconds: Socket connection and read timeout.
            max_tokens: Hard token generation cutoff.
        """
        self.endpoint_url = endpoint_url
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self.max_tokens = max_tokens

    def verify_small_model_comprehension(
        self, basic_prompt_content: str, catalog_path: str, compiler_module: Optional[Any] = None
    ) -> tuple[bool, str]:
        """Queries local MLX server and compiles returned DSL line.

        Args:
            basic_prompt_content: The mutated system instructions contract.
            catalog_path: Disk path to catalog schema JSON.
            compiler_module: Optional candidate ExpressCompiler class override.

        Returns:
            A tuple containing (PassedBoolean, ReasonString).
        """
        micro_target = [
            {
                "id": "submitBtn",
                "component": "Button",
                "properties": {"label": "Submit Deal", "action": "$/actions/submit"},
            }
        ]

        user_prompt = (
            f"Translate this component into a compact A2UI Express DSL assignment line:\n"
            f"{json.dumps(micro_target)}\n"
            f"Assignment line:"
        )

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": basic_prompt_content},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "max_tokens": self.max_tokens,
        }

        req = urllib.request.Request(
            self.endpoint_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                output_line = data["choices"][0]["message"]["content"].strip()
        except (urllib.error.URLError, TimeoutError, KeyError, IndexError) as e:
            return False, f"MLX server unreachable or timed out ({self.timeout_seconds}s limit): {e}"

        # Feed generated line into candidate compiler
        comp_cls = compiler_module if compiler_module else ExpressCompiler
        compiler = comp_cls(catalog_path)

        try:
            envelope = compiler.compile(output_line, surface_id="tier2_surf")
            comps = envelope.get("createSurface", {}).get("components", [])
            if not comps:
                return False, "Compiler produced empty component tree from MLX output"
            return True, f"Successfully parsed MLX line: {output_line}"
        except (SyntaxError, ValueError, KeyError) as e:
            return False, f"Candidate compiler failed to parse MLX line '{output_line}': {e}"
