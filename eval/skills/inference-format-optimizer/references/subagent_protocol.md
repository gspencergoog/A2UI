# Multi-Agent Subagent Worktree Protocol

This document specifies the execution protocol for running format optimization passes using autonomous subagents in isolated Git worktrees.

---

## 1. Worktree Isolation & Naming Convention

To prevent code conflicts and race conditions, each optimization pass runs in a dedicated Git worktree branch:

- **Branch Name Pattern**: `opt-<format>-pass<N>` (e.g., `opt-express-pass6`)
- **Directory Location**: `worktrees/opt-<format>-pass<N>` (e.g., `/usr/local/google/home/gspencer/code/a2ui/worktrees/opt-express-pass6`)

```bash
git worktree add -b opt-express-pass6 /usr/local/google/home/gspencer/code/a2ui/worktrees/opt-express-pass6 optimize_express
```

---

## 2. Subagent Launch via `invoke_subagent`

The parent agent launches subagents sequentially using `invoke_subagent`:

- **TypeName**: `"self"`
- **Role**: `"Express Pass <N> Optimizer"`
- **Workspace**: `"inherit"`

---

## 3. Subagent Execution Sequence

Each subagent MUST execute the following 5-step sequence inside its worktree:

1. **Implement Hypothesis**: Edit target compiler (`compiler.py`), prompt generator (`prompt_generator.py`), or parser (`parser.py`).
2. **Run Pytest Unit Tests**:
   ```bash
   PYTHONPATH=agent_sdks/python/a2ui_agent/src:agent_sdks/python/a2ui_core/src /usr/local/google/home/gspencer/code/a2ui/iterative_optimization/.venv/bin/python -m pytest agent_sdks/python/a2ui_agent/tests/<format>/
   ```
3. **Run Evaluation Benchmark**:
   ```bash
   /usr/local/google/home/gspencer/code/a2ui/iterative_optimization/.venv/bin/python eval/skills/inference-format-optimizer/scripts/optimize_format.py --format <format>
   ```
4. **Evaluate Decision Rules & Archive**:
   - If unit tests fail, Quality Score regresses, or Output Tokens expand $> +5\%$:
     ```bash
     git reset --hard HEAD
     /usr/local/google/home/gspencer/code/a2ui/iterative_optimization/.venv/bin/python eval/skills/inference-format-optimizer/scripts/optimize_format.py --format <format> --archive --hypothesis "..." --status REVERT --notes "<reason>"
     ```
   - Else:
     ```bash
     /usr/local/google/home/gspencer/code/a2ui/iterative_optimization/.venv/bin/python eval/skills/inference-format-optimizer/scripts/optimize_format.py --format <format> --archive --hypothesis "..." --status KEEP --notes "<summary>"
     ```
5. **Synchronize History Index**:
   ```bash
   /usr/local/google/home/gspencer/code/a2ui/iterative_optimization/.venv/bin/python eval/skills/inference-format-optimizer/scripts/sync_history.py
   ```

---

## 4. Parent Subagent Lifecycle Management

Once a subagent reports completion of its pass:
1. **Incorporate Results**: Record the pass metrics in the run log and git commit the kept changes if applicable.
2. **Terminate Subagent**: Call `manage_subagents(Action="kill", ConversationIds=[...])` for completed subagent IDs to prevent background resource accumulation.
3. **Clean Worktree**: Remove the temporary pass worktree (`git worktree remove --force ...`) and branch (`git branch -D ...`).
