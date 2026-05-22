#!/usr/bin/env python3

"""Command-line tool to generate prompt contracts for A2UI Express.

Crawls the specified catalog JSON schema and outputs a formatted model system prompt
containing complete instructions and positional signatures on stdout.
"""

import argparse
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from specification.v0_10.express.prompt_generator import ExpressPromptGenerator


def generate_prompt_text(catalog_path: str) -> str:
    """Generates the A2UI Express system prompt contract.

    Args:
        catalog_path: Path to the catalog JSON schema.

    Returns:
        The compiled system prompt text block.

    Raises:
        FileNotFoundError: If the catalog schema file does not exist.
    """
    if not os.path.exists(catalog_path):
        raise FileNotFoundError(f"Catalog schema not found: {catalog_path}")

    generator = ExpressPromptGenerator(catalog_path)
    return generator.generate_prompt()


def main():
    """CLI entrypoint for the prompt generator."""
    parser = argparse.ArgumentParser(
        description=
        "Generate model system prompts for A2UI Express from a catalog schema."
    )
    parser.add_argument(
        "--catalog",
        default=os.path.join(os.path.dirname(__file__), "..", "catalogs",
                             "basic", "catalog.json"),
        help="Path to the catalog JSON schema (default: basic catalog).")

    args = parser.parse_args()

    try:
        prompt_content = generate_prompt_text(args.catalog)
        print(prompt_content)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
