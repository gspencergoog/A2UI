#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-genai",
# ]
# ///
"""A temporary test script to verify direct model inference.

Sends a simple user prompt query to a specified Gemini or Gemma model and prints
the response text to standard output.
"""

import argparse
import os
import sys


def test_query(prompt: str, model_name: str):
    """Submits a direct prompt query to the model and prints its response.

    Args:
        prompt: The user prompt string.
        model_name: The model identifier.
    """
    try:
        # pylint: disable=import-outside-toplevel
        from google import genai
        # pylint: enable=import-outside-toplevel
    except ImportError as e:
        raise ImportError(
            "The 'google-genai' SDK is required. Install it via: pip install google-genai"
        ) from e

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    # Prepend models/ prefix if missing
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"

    client = genai.Client(api_key=api_key)
    print(f"Sending query to model '{model_name}'...")

    try:
        response = client.models.generate_content(model=model_name,
                                                  contents=prompt)
        print("\nResponse:")
        print(response.text)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"\nError during inference: {e}", file=sys.stderr)


def main():
    """CLI entrypoint for the direct model query test."""
    parser = argparse.ArgumentParser(
        description="Send a direct query prompt to a Gemini or Gemma model.")
    parser.add_argument("prompt",
                        help="The prompt query to send to the model.")
    parser.add_argument("--model",
                        default="gemma-4-31b-it",
                        help="Model name to run (default: gemma-4-31b-it).")

    args = parser.parse_args()
    test_query(args.prompt, args.model)


if __name__ == "__main__":
    main()
