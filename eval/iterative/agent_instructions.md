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

### Step 1: Analyze & Formulate Hypothesis
1. Check the baseline results under `eval/baselines/{format}/results.json`.
2. Scan the current optimization index `eval/iterative/history_summary.md` and read recent reports in `eval/iterative/history/` to understand past experiments and avoid duplicate/failing paths.
3. Identify a failure pattern (e.g. invalid syntax, schema violation, or grader grade of "I" or "P").
4. Formulate a hypothesis (e.g., "Adding negative examples in the system prompt will reduce redundant parent container generation").

### Step 2: Implement and Verify Code
1. Implement changes in:
   - System prompts and format rules: `agent_sdks/python/a2ui_agent/src/a2ui/inference_formats/experimental/{format}/prompt_generator.py` (or prompt template files).
   - Parser, compiler, or decompiler code: under `agent_sdks/python/a2ui_agent/src/a2ui/inference_formats/experimental/{format}/`.
2. Run pytest conformance unit tests locally first:
   ```bash
   uv run pytest agent_sdks/python/a2ui_agent/tests/
   ```
3. If unit tests fail, classify the failure:
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

### Step 4: Evaluate Metrics & Git Diff
Read the generated report in `eval/iterative/current_report.md`. Analyze:
1. **Pytest Conformance**: Must be `PASS`.
2. **Accuracies**: Overall Accuracy (LLM graded) and Algorithmic Schema Pass Rate.
3. **Resource footprints**:
   - `inference_duration_seconds` (latency)
   - `inference_input_tokens` (prompt size cost)
   - `inference_output_tokens` (generation size cost)
4. **Git Diff**: Verify that only the intended files were modified.

### Step 5: Progression or Rollback Decision
* **If accuracy degrades (or efficiency metrics spike significantly with no gain)**: You **must** roll back the changes using Git (`git reset --hard HEAD` or `git checkout -- <files>`). Document this as a failed/backtracked run in history.
* **If accuracy improves or remains neutral with clean conformance**: Keep the changes and prepare to archive.

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
