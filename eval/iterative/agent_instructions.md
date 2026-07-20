# Agent Instructions: Continuous Inference Format Optimization

You are an autonomous coding subagent tasked with systematically optimizing and improving an A2UI inference format (e.g., `atom`, `express`, `elemental`). Your goal is to maximize LLM generation pass rates (accuracy) while minimizing latency and token footprints.

---

## Workspace Setup

Before making edits, spin up an isolated git worktree branch to run your experiments without conflicting with parallel agent runs or main code:
```bash
# Branch name convention: opt-<format>-<hypothesis_slug>[-<agent_id>]
# Directory convention: ../worktrees/<branch_name>
git worktree add ../worktrees/opt-atom-brackets -b opt-atom-brackets
```
Execute all subsequent steps inside that worktree directory.

---

## The Optimization Loop

For each iteration, perform the following steps:

### Step 1: Analyze History & Formulate Hypothesis
1. **Check Historical Index & Past Runs**: Read `eval/iterative/history_summary.md` and scan recent `run_meta.json` files in `eval/iterative/history/` to inspect all previous experiments, their hypotheses, status (`KEEP` vs `REVERT`), and code diffs.
2. **Anti-Repetition Constraint**: **DO NOT** repeat or retry a hypothesis, prompt rule edit, or code modification that was already tested and reverted in a past run.
3. **Analyze Failure Patterns**: Review baseline failure logs in `eval/baselines/{format}/results.json` to identify unresolved failure patterns (e.g. nested layout errors, dangling string references, missing optional attributes).
4. **Formulate a Minimal Hypothesis**: State a specific, targeted hypothesis (e.g. "Replacing positional parameter placeholders with explicit keyword syntax will eliminate container nesting ambiguity").

### Step 2: Implement and Verify Code
1. Implement changes in:
   - System prompts and format rules: `agent_sdks/python/a2ui_agent/src/a2ui/inference_formats/experimental/{format}/prompt_generator.py` (or prompt template files).
   - Parser, compiler, or decompiler code: under `agent_sdks/python/a2ui_agent/src/a2ui/inference_formats/experimental/{format}/`.
2. Run pytest conformance unit tests locally first:
   ```bash
   uv run pytest agent_sdks/python/a2ui_agent/tests/
   ```
3. If unit tests fail, classify the failure:
   - **Prompt-Only Regression**: If only prompt/template files were modified and unit tests fail, it is a prompt regression. You **MUST** immediately revert the prompt modification.
   - **Parser/Compiler Regression**: A change broke existing valid compiler behavior. You **must** fix the compiler code or revert the change.
   - **Format Capability Evolution**: The compiler was deliberately modified to support new/updated syntax, causing old tests to fail. You **must** update the unit tests under `agent_sdks/python/a2ui_agent/tests/{format}/` to match and cover the new capability.

### Step 3: Run the Evaluation
Run the orchestrator script to compile the metrics and generate the current diagnostic report. By default, this runs on a small-scale validation subset of 5 diverse prompts to minimize cost and execution time:
```bash
uv run python eval/iterative/optimize_format.py --format <format> --model <model>
```
*Note: For targeted debugging of a specific failure, you can run:*
```bash
uv run python eval/iterative/optimize_format.py --format <format> --model <model> --prompt <prompt_name>
```

### Step 4: Evaluate Metrics & Compare Against Baseline
Run `compare_results.py` to compare your current run directory against the baseline directory (`eval/baselines/transport` or `eval/baselines/<format>`). By default, it computes median metrics:
```bash
uv run python eval/iterative/compare_results.py --baseline eval/baselines/<format> <current_run_dir_or_eval_log>
```
*(To inspect mean averages instead of default medians, pass `--average`)*.

Analyze the generated Markdown table and Metric Definitions Key:
1. **Pytest Conformance**: Must be `PASS`.
2. **Correctness Guardrails**:
   - `Schema Acc (Delta)`: Percentage of outputs passing strict compiler syntax and schema validation (`a2ui_scorer`).
   - `Quality Score (Delta)`: LLM-graded semantic intent accuracy score (`measured_model_graded_qa`).
3. **Efficiency Optimization Metrics**:
   - `Median Code Output Tok (Delta)`: Token count of generated code. Direct target of format design optimization.
   - `Non-reasoning Output Time (Median)`: Estimated time spent emitting code. Shrinks proportionally with code output tokens.
   - `Median Input Tok (Delta)`: System prompt and catalog schema token size. Lower input tokens prevent API throttling.
   - `Parallel Wall Latency (Delta)`: Batch wall-clock throughput under 10 concurrent tasks.

### Step 5: Progression or Rollback Decision
Evaluate your iteration against these 3 decision rules:
1. **Rule 1 (Correctness Guardrail - Non-negotiable)**: `Schema Acc` and `Quality Score` **MUST NOT** regress below Baseline.
   - *If Accuracy Degrades* $\rightarrow$ You **MUST** immediately roll back the changes (`git reset --hard HEAD`).
2. **Rule 2 (Code Footprint)**: Did `Median Code Output Tok` decrease without degrading accuracy?
   - *If YES* $\rightarrow$ **KEEP CHANGE** (The format is demonstrably more compact).
3. **Rule 3 (Prompt Overhead)**: Did `Median Input Tok` decrease without degrading accuracy?
   - *If YES* $\rightarrow$ **KEEP CHANGE** (The prompt instructions are more concise).

### Step 6: Archive Iteration Run
To save the historical run context for future analysis and allow the orchestrator to automatically maintain the summary index:
1. Determine the next run index (e.g. `run_003`).
2. Create the run folder:
   ```bash
   # Directory naming: run_<three_digit_index>_<commit_sha>_<slugified_summary>
   mkdir -p eval/iterative/history/run_003_a8f9c1b_fix_brackets
   ```
3. Archive logs and files:
   - Copy report: `cp eval/iterative/current_report.md eval/iterative/history/run_003_a8f9c1b_fix_brackets/report.md`
   - Copy results log: `cp eval/logs/temp_optimization/results.json eval/iterative/history/run_003_a8f9c1b_fix_brackets/results.json`
   - Generate diff patch: `git diff > eval/iterative/history/run_003_a8f9c1b_fix_brackets/patch.diff`
4. Write `run_meta.json` folder metadata detailing your hypothesis and annotations:
   ```json
   {
     "hypothesis": "Description of proposed fix",
     "notes": "Qualitative summary of results / failures",
     "status": "Kept" (or "Backtracked")
   }
   ```
5. Commit the code and the archived folder local to your branch.

---

## Verification & Merging

1. **Full Suite Check**: Once the small-scale validation set achieves 100% success (or plateaus), run a full verification across the entire 50+ prompt evaluation suite:
   ```bash
   uv run python eval/iterative/optimize_format.py --format <format> --model <model> --full
   ```
2. **PR creation**: Create a Pull Request to merge your worktree branch back to the main repository. When branches are merged, the history run folders merge conflict-free. The index `history_summary.md` will be rebuilt automatically on the next execution.

---

## Termination Triggers

Stop your execution loop and report results to the human operator when:
1. **Target Achieved**: 100% pass rate is achieved on the full suite.
2. **Plateau**: No accuracy improvements are observed after 3 consecutive iterations with different hypotheses.
3. **Max Iterations**: You have completed 10 runs.
4. **Stuck / Blocked**: If you encounter an infrastructure error or a requirement conflict that prompt/compiler tuning cannot fix, halt and ask for help.
