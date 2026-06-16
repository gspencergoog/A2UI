# A2UI Express developer guide

A2UI Express is a compact, token-efficient declarative syntax designed for dynamic generative user interfaces. It acts as an intermediate, highly compressed notation that local on-device models generate. A host-side compiler parses this syntax and compiles it into standard A2UI v1.0 wire protocol payloads.

This guide explains how to install the native Apple Silicon MLX local model runner, boot a local Gemma 4 completions server, and run compilation validation.

## Local model setup

To run the latest multimodal Gemma 4 models with hardware acceleration on Apple Silicon, developers use Apple's **mlx-vlm** framework.

### Installing the framework

Next, install the `mlx-vlm` package globally using the standard corporate Artifact Registry package index:

```bash
uv tool install --force mlx-vlm
```

This installs the framework and registers its CLI utilities in your user executable path, including `mlx_vlm.server` and `mlx_vlm.generate`.

### Starting the Gemma 4 completions server

Spin up the local completions server using the 4-bit quantized Gemma 4 E2B model. This E2B size is optimized for memory footprint and generation speed on developer workstations:

```bash
mlx_vlm.server --model mlx-community/gemma-4-e2b-it-4bit --port 8080
```

On startup, the server retrieves the weights from Hugging Face Hub, caches them locally in your home directory (`~/.cache/huggingface/`), and boots an OpenAI-compatible completions API endpoint on `http://localhost:8080`.

---

## Compiling dynamic user interfaces

Once the local Gemma 4 server is active, you can run the end-to-end compilation and validation pipeline.

### Running local inference and validation

To test local generation and compiler correctness in a single command, run the inference script with the `--mlx` flag:

```bash
# Navigate to the express directory
cd main/specification/v1_0/express

# Run inference against your local Gemma 4 server
uv run ./run_inference.py \
  ../catalogs/basic/examples/01_flight-status.json \
  --mlx
```

The script will:

1. Extract the target component structure from the JSON example.
2. Compile the active catalog schema definitions into plain-text positional signatures.
3. Query your local Gemma 4 server at `http://localhost:8080/v1/chat/completions`.
4. Compile the returned A2UI Express DSL back into pretty-printed, standard A2UI v1.0 JSON.
5. Validate the final component tree structure, checking parent-child references and data pointer paths.

---

## CLI utility reference

The `express` package provides three standalone developer scripts. Each script dynamically adjusts python paths during execution, allowing them to run directly from any directory.

### Direct prompt generation

Generate the model prompt contract, containing positional component signatures and rules compiled from the active catalog schema:

```bash
# Direct execution from any path
./run_prompt_generator.py --catalog ../catalogs/basic/catalog.json
```

### Plain DSL compiler

Compile an offline A2UI Express DSL file directly into standard pretty-printed v1.0 JSON:

```bash
./run_compiler.py \
  path/to/sample.express \
  --surface-id "dashboard_surface"
```

### JSON-to-Express decompiler

Convert standard A2UI v1.0 JSON envelopes back into compact A2UI Express code:

```bash
./run_decompiler.py ../catalogs/basic/examples/01_flight-status.json
```
