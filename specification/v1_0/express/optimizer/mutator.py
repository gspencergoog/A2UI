"""Mutation engine and automated AST self-repair loop for A2UI Express optimizer.

Injects reigning champion artifacts into mutate_prompt.md, submits conversion
requests to Gemini, extracts XML blocks, and verifies Python syntax integrity.
"""

import ast
import os
import re
import subprocess
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

    def __init__(self, prompt_template_path: str, model_name: str = "gemini-3.1-pro-preview", thinking_budget: int = 16384):
        """Initializes the mutator with prompt template, target model, and thinking budget.

        Args:
            prompt_template_path: Disk path to mutate_prompt.md.
            model_name: Target Gemini model identifier.
            thinking_budget: Token allocation for internal chain-of-thought scratchpad.
        """
        self.prompt_template_path = prompt_template_path
        self.model_name = "gemini-3.1-pro-preview" if model_name == "gemini-3-pro-preview" else model_name
        self.thinking_budget = thinking_budget
        with open(prompt_template_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

        self.client = genai.Client() if genai else None

    def _extract_xml_block(self, text: str, tag: str) -> Optional[str]:
        """Extracts content enclosed within specific XML tags."""
        match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
        return match.group(1).strip() if match else None

    def _apply_patch_block(self, source: str, patch_xml: Optional[str]) -> str:
        """Applies a search-and-replace patch block programmatically."""
        if not patch_xml:
            return source

        targets = re.findall(r"<target>\s*(.*?)\s*</target>", patch_xml, re.DOTALL)
        replacements = re.findall(r"<replacement>\s*(.*?)\s*</replacement>", patch_xml, re.DOTALL)

        if len(targets) != len(replacements):
            raise ValueError("Mismatched count of <target> and <replacement> tags in patch block.")

        cur = source
        for t, r in zip(targets, replacements):
            if t not in cur:
                t_sub = t.strip("\r\n")
                if t_sub not in cur:
                    raise ValueError(f"Patch target snippet not found in source:\n{t[:100]}")
                cur = cur.replace(t_sub, r.strip("\r\n"))
            else:
                cur = cur.replace(t, r)

        return cur

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

        prompt_gen_path = os.path.join(os.path.dirname(__file__), "..", "prompt_generator.py")
        with open(prompt_gen_path, "r", encoding="utf-8") as f:
            prompt_gen_content = f.read()

        prompt = self.prompt_template.format(
            A2UI_EXPRESS_CONTENT=champion.a2ui_express_content,
            PROMPT_GENERATOR_CONTENT=prompt_gen_content,
            COMPILER_CONTENT=champion.compiler_content,
            DECOMPILER_CONTENT=champion.decompiler_content,
        )

        messages = [
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        ]

        for attempt in range(1, max_retries + 1):
            output_text = None
            try:
                if attempt == 1:
                    config = (
                        types.GenerateContentConfig(
                            thinking_config=types.ThinkingConfig(thinking_budget=self.thinking_budget),
                            temperature=0.7,
                        )
                        if types else None
                    )
                else:
                    config = (
                        types.GenerateContentConfig(
                            thinking_config=types.ThinkingConfig(thinking_budget=2048),
                            temperature=0.3,
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
                        if any(k in err_str for k in ("429", "503", "504", "quota", "exhausted", "reset", "connection", "timeout", "readerror")):
                            print(f"API Rate limit hit on attempt {attempt} ({api_err}). Backing off for {backoff_sec}s...")
                            time.sleep(backoff_sec)
                            backoff_sec *= 2.0
                        else:
                            raise api_err
                else:
                    raise RuntimeError("Exhausted 5 API exponential backoff retries due to persistent rate limiting.")

                output_text = response.text

                a2ui_spec = self._extract_xml_block(output_text, "a2ui_express.md")
                prompt_gen_patch = (
                    self._extract_xml_block(output_text, "prompt_generator_patch") or
                    self._extract_xml_block(output_text, "prompt_generator_instructions")
                )
                compiler_patch = (
                    self._extract_xml_block(output_text, "compiler_patch") or
                    self._extract_xml_block(output_text, "compiler_instructions")
                )
                decompiler_patch = (
                    self._extract_xml_block(output_text, "decompiler_patch") or
                    self._extract_xml_block(output_text, "decompiler_instructions")
                )

                if not a2ui_spec:
                    raise ValueError("Missing mandatory <a2ui_express.md> XML block.")

                if target_disk_dir:
                    os.makedirs(target_disk_dir, exist_ok=True)
                    with open(os.path.join(target_disk_dir, "refactoring_instructions.json"), "w", encoding="utf-8") as pf:
                        json.dump({
                            "prompt_generator": prompt_gen_patch,
                            "compiler": compiler_patch,
                            "decompiler": decompiler_patch
                        }, pf, indent=2)

                prompt_gen_code = self._apply_patch_block(prompt_gen_content, prompt_gen_patch)
                compiler_code = self._apply_patch_block(champion.compiler_content, compiler_patch)
                decompiler_code = self._apply_patch_block(champion.decompiler_content, decompiler_patch)

                # AST Robustness Gate (Self-Repair Trigger)
                ast.parse(prompt_gen_code)
                ast.parse(compiler_code)
                ast.parse(decompiler_code)

                # Dynamically execute mutated prompt generator in-memory
                spec_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                catalog_path = os.path.join(spec_dir, "..", "catalogs", "basic", "catalog.json")
                namespace = {"__package__": "specification.v1_0.express"}
                exec(prompt_gen_code, namespace)
                generator = namespace["ExpressPromptGenerator"](catalog_path)
                basic_prompt = generator.generate_prompt()

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
                if not gauntlet._run_local_unit_tests(offspring)[0]:
                    raise SyntaxError(
                        "Your generated compiler parser failed in-memory Tier 0/1 compilation unit tests "
                        "against reference golden targets. Inspect syntax rules and logic."
                    )

                # Stage 2: Actor-Critic Critique and Review Pass
                critique_prompt = (
                    "Review your proposed A2UI Express specification, system prompt, AST parser, and decompiler.\n"
                    "Ensure that:\n"
                    "1. All mandatory catalog component signatures (Button, Card, Column, Icon, Row, Text, TextField) remain fully documented in basic_prompt.md.\n"
                    "2. Unquoted string parsing rules do not collide with component identifiers, boolean literals (true/false), or null.\n"
                    "3. Parsing and decompilation logic is robust against extra whitespace and backticks.\n"
                    "Output the final polished and verified four XML blocks precisely."
                )
                messages.append(
                    types.Content(role="model", parts=[types.Part.from_text(text=output_text)])
                )
                messages.append(
                    types.Content(role="user", parts=[types.Part.from_text(text=critique_prompt)])
                )
                print("Executing Stage 2 Actor-Critic Review Pass...")
                critique_response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=messages,
                    config=config,
                )
                crit_out = critique_response.text
                c_spec = self._extract_xml_block(crit_out, "a2ui_express.md")
                c_prompt = self._extract_xml_block(crit_out, "basic_prompt.md")
                c_comp = self._extract_xml_block(crit_out, "compiler.py")
                c_dec = self._extract_xml_block(crit_out, "decompiler.py")

                if c_spec and c_prompt and c_comp and c_dec:
                    try:
                        ast.parse(c_comp)
                        ast.parse(c_dec)
                        offspring.a2ui_express_content = c_spec
                        offspring.basic_prompt_content = c_prompt
                        offspring.compiler_content = c_comp
                        offspring.decompiler_content = c_dec
                        offspring.gene_id = f"gene_{offspring.compute_hash()}"
                    except SyntaxError:
                        pass

                if target_disk_dir:
                    offspring.save_to_disk(target_disk_dir)

                return offspring

            except Exception as e:
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
