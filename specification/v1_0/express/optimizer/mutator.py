"""Mutation engine and automated AST self-repair loop for A2UI Express optimizer.

Injects reigning champion artifacts into mutate_prompt.md, submits conversion
requests to Gemini, extracts XML blocks, and verifies Python syntax integrity.
"""

import ast
import re
import sys
import time
import traceback
from typing import Optional

try:
    # pylint: disable=import-error
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

from .gauntlet import EvaluationGauntlet
from .manifest import Gene


class ExpressMutator:
    """Orchestrates LLM mutations with automated syntax self-repair."""

    def __init__(self, prompt_template_path: str, model_name: str = "gemini-pro-latest", thinking_budget: int = 8192):
        """Initializes the mutator with prompt template, target model, and thinking budget.

        Args:
            prompt_template_path: Disk path to mutate_prompt.md.
            model_name: Target Gemini model identifier.
            thinking_budget: Token allocation for internal chain-of-thought scratchpad.
        """
        self.prompt_template_path = prompt_template_path
        self.model_name = model_name
        self.thinking_budget = thinking_budget
        with open(prompt_template_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

        self.client = genai.Client() if genai else None

    def _extract_xml_block(self, text: str, tag: str) -> Optional[str]:
        """Extracts content enclosed within specific XML tags."""
        match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
        return match.group(1).strip() if match else None

    def generate_mutation(
        self, champion: Gene, max_retries: int = 3, target_disk_dir: Optional[str] = None
    ) -> Optional[Gene]:
        """Generates a candidate mutation bundle, self-repairing AST syntax errors.

        Args:
            champion: The reigning champion Gene baseline.
            max_retries: Maximum syntax repair retry attempts.
            target_disk_dir: Optional disk path to serialize winning bundles.

        Returns:
            The successfully parsed and validated offspring Gene, or None if failed.
        """
        if not self.client:
            print("Warning: google-genai SDK not available. Skipping mutation API call.")
            return None

        prompt = self.prompt_template.format(
            A2UI_EXPRESS_CONTENT=champion.a2ui_express_content,
            BASIC_PROMPT_CONTENT=champion.basic_prompt_content,
            COMPILER_CONTENT=champion.compiler_content,
            DECOMPILER_CONTENT=champion.decompiler_content,
        )

        messages = [
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        ]

        for attempt in range(1, max_retries + 1):
            output_text = None
            try:
                config = (
                    types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=self.thinking_budget),
                        temperature=0.7,
                    )
                    if types else None
                )

                # API Rate Limit Protection with Exponential Backoff
                backoff_sec = 4.0
                for backoff_attempt in range(5):
                    try:
                        response = self.client.models.generate_content(
                            model=self.model_name,
                            contents=messages,
                            config=config,
                        )
                        break
                    except Exception as api_err:
                        err_str = str(api_err).lower()
                        if "429" in err_str or "503" in err_str or "quota" in err_str or "exhausted" in err_str:
                            print(f"API Rate limit hit on attempt {attempt} ({api_err}). Backing off for {backoff_sec}s...")
                            time.sleep(backoff_sec)
                            backoff_sec *= 2.0
                        else:
                            raise api_err
                else:
                    raise RuntimeError("Exhausted 5 API exponential backoff retries due to persistent rate limiting.")

                output_text = response.text

                a2ui_spec = self._extract_xml_block(output_text, "a2ui_express.md")
                basic_prompt = self._extract_xml_block(output_text, "basic_prompt.md")
                compiler_code = self._extract_xml_block(output_text, "compiler.py")
                decompiler_code = self._extract_xml_block(output_text, "decompiler.py")

                if not all([a2ui_spec, basic_prompt, compiler_code, decompiler_code]):
                    raise ValueError("Failed to extract all four mandatory XML blocks.")

                # AST Robustness Gate (Self-Repair Trigger)
                ast.parse(compiler_code)
                ast.parse(decompiler_code)

                # Syntax is clean. Construct offspring bundle.
                offspring = Gene(
                    gene_id="",  # Will be populated after hash computation
                    a2ui_express_content=a2ui_spec,
                    basic_prompt_content=basic_prompt,
                    compiler_content=compiler_code,
                    decompiler_content=decompiler_code,
                    parent_id=champion.gene_id,
                )
                offspring.gene_id = f"gene_{offspring.compute_hash()}"

                # Tier 0/1 Compilation Gauntlet Gate (Self-Repair Trigger)
                gauntlet = EvaluationGauntlet()
                if not gauntlet._run_local_unit_tests(offspring):
                    raise SyntaxError(
                        "Your generated compiler parser failed in-memory Tier 0/1 compilation unit tests "
                        "against reference golden targets. Inspect syntax rules and logic."
                    )

                if target_disk_dir:
                    offspring.save_to_disk(target_disk_dir)

                return offspring

            except (SyntaxError, ValueError) as e:
                print(f"Mutation attempt {attempt} failed syntax/extraction validation: {e}")
                if attempt == max_retries:
                    print("Max syntax self-repair retries exhausted. Discarding candidate.")
                    return None

                exc_str = "".join(traceback.format_exception(*sys.exc_info()))
                repair_prompt = (
                    f"Your previous output failed validation with the following error:\n"
                    f"{exc_str}\n"
                    f"Inspect the Python syntax and XML structure, fix the errors, and "
                    f"resubmit precisely the four corrected XML blocks."
                )
                if output_text:
                    messages.append(
                        types.Content(role="model", parts=[types.Part.from_text(text=output_text)])
                    )
                messages.append(
                    types.Content(role="user", parts=[types.Part.from_text(text=repair_prompt)])
                )

        return None
