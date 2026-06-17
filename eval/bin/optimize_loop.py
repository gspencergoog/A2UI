#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import glob
import json
import zipfile
import subprocess
import argparse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
TMP_DIR = os.path.join(WORKSPACE_ROOT, "tmp")

os.makedirs(TMP_DIR, exist_ok=True)

def find_latest_eval_file(log_dir_name=None):
    """Finds the latest .eval file in the specified log subdirectory or globally."""
    base_logs = os.path.join(WORKSPACE_ROOT, "eval/logs")
    search_path = os.path.join(base_logs, "*.eval")
    if log_dir_name:
        search_path = os.path.join(base_logs, log_dir_name, "*.eval")
        
    eval_files = glob.glob(search_path)
    if not log_dir_name:
        # Also check subdirectories
        for d in os.listdir(base_logs):
            sub = os.path.join(base_logs, d)
            if os.path.isdir(sub):
                eval_files.extend(glob.glob(os.path.join(sub, "*.eval")))
                
    if not eval_files:
        return None
    # Sort by modification time
    eval_files.sort(key=os.path.getmtime, reverse=True)
    return eval_files[0]

try:
    import zstandard
except ImportError:
    pass
try:
    import inspect_ai
except ImportError:
    pass

def analyze_failures(eval_file_path):
    """Extracts failed samples from a .eval zip file and saves them to tmp/failed_samples.json."""
    if not eval_file_path:
        print("Error: No evaluation file provided.")
        sys.exit(1)
        
    print(f"Analyzing failures from: {eval_file_path}")
    failures = []
    
    with zipfile.ZipFile(eval_file_path, "r") as z:
        sample_files = [name for name in z.namelist() if name.startswith("samples/") and name.endswith(".json")]
        
        for s_file in sample_files:
            try:
                sample = json.loads(z.read(s_file))
            except Exception as e:
                print(f"Error reading {s_file}: {e}")
                continue
                
            scores = sample.get("scores", {})
            
            a2ui_score_obj = scores.get("a2ui_scorer", {})
            a2ui_val = a2ui_score_obj.get("value", 0.0)
            if isinstance(a2ui_val, str):
                a2ui_val = 1.0 if a2ui_val == "C" else (0.5 if a2ui_val == "P" else 0.0)
                
            qa_score_obj = scores.get("measured_model_graded_qa", {})
            qa_val = qa_score_obj.get("value", 0.0)
            if isinstance(qa_val, str):
                qa_val = 1.0 if qa_val == "C" else (0.5 if qa_val == "P" else 0.0)
                
            if a2ui_val < 1.0 or qa_val < 1.0:
                # Find raw DSL in messages
                messages = sample.get("messages", [])
                raw_dsl = None
                for msg in reversed(messages):
                    if msg.get("role") == "assistant":
                        content = msg.get("content")
                        if isinstance(content, list):
                            parts = [p.get("text", "") for p in content if p.get("type") == "text"]
                            raw_dsl = "".join(parts)
                        else:
                            raw_dsl = content
                        break
                
                failures.append({
                    "id": sample.get("id"),
                    "input": sample.get("input"),
                    "target": sample.get("target"),
                    "raw_dsl": raw_dsl,
                    "syntax_score": a2ui_val,
                    "syntax_explanation": a2ui_score_obj.get("explanation"),
                    "qa_score": qa_val,
                    "qa_explanation": qa_score_obj.get("explanation")
                })
                
    output_path = os.path.join(TMP_DIR, "failed_samples.json")
    with open(output_path, "w") as f:
        json.dump(failures, f, indent=2)
    print(f"Extracted {len(failures)} failed samples to: {output_path}")
    return failures

MUTATE_PROMPT = """You are an AI optimization agent improving a layout generation system.
We have an evaluation run of a Domain-Specific Language (DSL) called "A2UI Express" that translates high-level prompts into standard A2UI JSON wire format.

We analyzed the failures of the latest run. Below is the list of failed test cases:
{failures_json}

Below is the current system prompt generator code ('agent_sdks/python/a2ui_agent/src/a2ui/express/prompt_generator.py'):
{prompt_generator_code}

Below is the current compiler code ('agent_sdks/python/a2ui_agent/src/a2ui/express/compiler.py'):
{compiler_code}

Based on these failures, propose up to 3 candidate mutations (mutually exclusive proposals) that could fix these errors.
Each mutation must target either the system prompt instructions inside `prompt_generator.py`, or code logic inside `compiler.py` (or both).
Focus on making specific, small, high-impact edits.

For each candidate, output a JSON object with:
1. `name`: Short name, e.g. "fix_card_nesting" or "clarify_list_binding".
2. `description`: 2-3 sentences explaining the rationale.
3. `mutations`: A list of file edits, each containing:
   - `file`: Path relative to workspace root (e.g. `agent_sdks/python/a2ui_agent/src/a2ui/express/prompt_generator.py`).
   - `search`: The exact contiguous lines of code to find.
   - `replace`: The replacement lines of code.

Output the final answer strictly as a JSON array of candidates.
"""

def generate_mutations(num_candidates=3):
    from google import genai
    from google.genai import types

    # Read failed samples
    failed_path = os.path.join(TMP_DIR, "failed_samples.json")
    if not os.path.exists(failed_path):
        print("Error: No failed_samples.json found. Run 'analyze' command first.")
        sys.exit(1)
    with open(failed_path, "r") as f:
        failures = json.load(f)
        
    if not failures:
        print("No failures found to mutate.")
        return []
        
    # Limit failures to first 10 to fit context window and keep it fast
    failures_json = json.dumps(failures[:10], indent=2)
    
    # Read files
    pg_path = os.path.join(WORKSPACE_ROOT, "agent_sdks/python/a2ui_agent/src/a2ui/express/prompt_generator.py")
    with open(pg_path, "r") as f:
        prompt_generator_code = f.read()
        
    compiler_path = os.path.join(WORKSPACE_ROOT, "agent_sdks/python/a2ui_agent/src/a2ui/express/compiler.py")
    with open(compiler_path, "r") as f:
        compiler_code = f.read()
        
    # Query Gemini
    print("Querying Gemini to generate mutation candidates...")
    client = genai.Client()
    prompt = MUTATE_PROMPT.format(
        failures_json=failures_json,
        prompt_generator_code=prompt_generator_code,
        compiler_code=compiler_code
    )
    
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )
    )
    
    # Parse candidates
    try:
        candidates = json.loads(response.text)
    except Exception as e:
        print(f"Error parsing Gemini response as JSON: {e}")
        print("Raw response:")
        print(response.text)
        sys.exit(1)
        
    candidates_path = os.path.join(TMP_DIR, "mutation_candidates.json")
    with open(candidates_path, "w") as f:
        json.dump(candidates, f, indent=2)
        
    print(f"Proposed {len(candidates)} mutation candidates. Saved to: {candidates_path}")
    return candidates

def apply_mutation_to_branch(candidate_index):
    candidates_path = os.path.join(TMP_DIR, "mutation_candidates.json")
    if not os.path.exists(candidates_path):
        print("Error: No mutation candidates found.")
        sys.exit(1)
    with open(candidates_path, "r") as f:
        candidates = json.load(f)
        
    if candidate_index < 0 or candidate_index >= len(candidates):
        print(f"Error: Candidate index {candidate_index} out of range.")
        sys.exit(1)
        
    cand = candidates[candidate_index]
    branch_name = f"express_mut_{cand.get('name')}"
    print(f"Applying candidate '{cand.get('name')}' to branch '{branch_name}'...")
    
    # Ensure working tree is clean
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
    if status.stdout.strip():
        print("Warning: Stashing unstaged changes in parent repository...")
        subprocess.run(["git", "stash"], check=True)
        
    # Checkout target branch
    subprocess.run(["git", "checkout", "a2ui_express_iterate"], check=True)
    # Delete branch if it exists, then recreate
    subprocess.run(["git", "branch", "-D", branch_name], stderr=subprocess.DEVNULL)
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    
    # Apply file replacements
    for mut in cand.get("mutations", []):
        file_rel = mut.get("file")
        file_abs = os.path.join(WORKSPACE_ROOT, file_rel)
        search_txt = mut.get("search")
        replace_txt = mut.get("replace")
        
        if not os.path.exists(file_abs):
            print(f"Error: Target file {file_abs} not found.")
            continue
            
        with open(file_abs, "r") as f:
            content = f.read()
            
        if search_txt not in content:
            print(f"Warning: Search block not found in {file_rel}. Skipping.")
            continue
            
        new_content = content.replace(search_txt, replace_txt)
        with open(file_abs, "w") as f:
            f.write(new_content)
        print(f"Successfully modified {file_rel}")
        
    # Commit changes
    subprocess.run(["git", "add", "-u"], check=True)
    subprocess.run(["git", "commit", "-m", f"opt(express): apply mutation candidate {cand.get('name')}"], check=True)
    
    # Revert to base branch in the parent workspace to keep it clean
    subprocess.run(["git", "checkout", "a2ui_express_iterate"], check=True)
    print(f"Branch '{branch_name}' created and committed!")

def print_orchestration_plan(candidates):
    print("\n" + "="*80)
    print("ORCHESTRATION PLAN FOR PARALLEL EVALUATIONS")
    print("="*80)
    print("Run the evaluations in parallel by executing the following subagents concurrently.\n")
    
    subagents_arg = []
    for cand in candidates:
        name = cand.get("name")
        branch_name = f"express_mut_{name}"
        prompt_str = (
            f"Please run the layout generation evaluation for the Express strategy on branch '{branch_name}':\n"
            f"1. Checkout branch '{branch_name}' inside your workspace:\n"
            f"   git checkout {branch_name}\n"
            f"2. Run the Inspect AI evaluation suite:\n"
            f"   uv run main.py --strategies express --log-dir logs/run_{name}\n"
            f"3. Return the exact evaluation summary line (including accuracy and tokens) as your final response."
        )
        subagents_arg.append({
            "TypeName": "self",
            "Role": f"EvalRunner-{name}",
            "Prompt": prompt_str,
            "Workspace": "branch"
        })
        
    print(json.dumps({"Subagents": subagents_arg}, indent=2))
    print("="*80 + "\n")

def extract_metrics_from_eval(eval_file_path):
    """Extracts accuracy and token count from an Inspect AI .eval file."""
    with zipfile.ZipFile(eval_file_path, "r") as z:
        summaries_data = json.loads(z.read("summaries.json"))
        
    a2ui_scores = []
    qa_scores = []
    total_input_tokens = 0
    total_output_tokens = 0
    total_reasoning_tokens = 0
    
    for sample in summaries_data:
        scores = sample.get("scores", {})
        
        # a2ui_scorer
        a2ui_obj = scores.get("a2ui_scorer", {})
        a2ui_val = a2ui_obj.get("value", 0.0)
        if isinstance(a2ui_val, str):
            a2ui_val = 1.0 if a2ui_val == "C" else (0.5 if a2ui_val == "P" else 0.0)
        a2ui_scores.append(a2ui_val)
        
        # measured_model_graded_qa
        qa_obj = scores.get("measured_model_graded_qa", {})
        qa_val = qa_obj.get("value", 0.0)
        if isinstance(qa_val, str):
            qa_val = 1.0 if qa_val == "C" else (0.5 if qa_val == "P" else 0.0)
        qa_scores.append(qa_val)
        
        # model usage
        usage = sample.get("model_usage", {})
        for model, counts in usage.items():
            total_input_tokens += counts.get("input_tokens", 0)
            total_output_tokens += counts.get("output_tokens", 0)
            total_reasoning_tokens += counts.get("reasoning_tokens", 0)
            
    a2ui_accuracy = sum(a2ui_scores) / len(a2ui_scores) if a2ui_scores else 0.0
    qa_accuracy = sum(qa_scores) / len(qa_scores) if qa_scores else 0.0
    total_tokens = total_input_tokens + total_output_tokens + total_reasoning_tokens
    
    return {
        "a2ui_accuracy": a2ui_accuracy,
        "qa_accuracy": qa_accuracy,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "reasoning_tokens": total_reasoning_tokens,
        "total_tokens": total_tokens
    }

def run_evals():
    """Runs evaluations sequentially for each candidate branch and extracts metrics."""
    candidates_path = os.path.join(TMP_DIR, "mutation_candidates.json")
    if not os.path.exists(candidates_path):
        print("Error: No mutation candidates found. Run 'mutate' command first.")
        sys.exit(1)
    with open(candidates_path, "r") as f:
        candidates = json.load(f)
        
    results = {}
    
    for cand in candidates:
        name = cand.get("name")
        branch_name = f"express_mut_{name}"
        log_dir = f"run_{name}"
        
        print("\n" + "="*60)
        print(f"RUNNING EVALUATION FOR CANDIDATE: {name}")
        print(f"Checking out branch {branch_name}...")
        print("="*60)
        
        # Checkout branch
        subprocess.run(["git", "checkout", branch_name], check=True)
        
        # Run eval command
        cmd = [
            "uv", "run", "main.py",
            "--strategies", "express",
            "--log-dir", f"logs/{log_dir}"
        ]
        print(f"Executing: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=os.path.join(WORKSPACE_ROOT, "eval"), check=True)
        
        # Find latest log file in logs/log_dir
        latest_eval = find_latest_eval_file(log_dir)
        if not latest_eval:
            print(f"Error: No evaluation log found for candidate {name}")
            continue
            
        metrics = extract_metrics_from_eval(latest_eval)
        results[name] = metrics
        print(f"Candidate {name} results extracted: {metrics}")
        
    # Revert to base branch
    subprocess.run(["git", "checkout", "a2ui_express_iterate"], check=True)
    
    # Save results
    results_path = os.path.join(TMP_DIR, "eval_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
        
    # Print summary table
    print("\n" + "="*80)
    print("EVALUATION RESULTS SUMMARY TABLE")
    print("="*80)
    print(f"{'Candidate Name':<50} | {'Syntax Acc':<10} | {'QA Acc':<10} | {'Total Tokens':<12}")
    print("-" * 90)
    for name, m in results.items():
        print(f"{name:<50} | {m['a2ui_accuracy']:<10.3f} | {m['qa_accuracy']:<10.3f} | {m['total_tokens']:<12,}")
    print("="*80 + "\n")

def select_best():
    """Selects the best mutation candidate, merges it, and deletes the other candidate branches."""
    results_path = os.path.join(TMP_DIR, "eval_results.json")
    if not os.path.exists(results_path):
        print("Error: No evaluation results found. Run 'run-evals' command first.")
        sys.exit(1)
    with open(results_path, "r") as f:
        results = json.load(f)
        
    candidates_path = os.path.join(TMP_DIR, "mutation_candidates.json")
    with open(candidates_path, "r") as f:
        candidates = json.load(f)
        
    if not results:
        print("No evaluation results found.")
        sys.exit(1)
        
    best_candidate = None
    best_qa = -1.0
    best_syntax = -1.0
    best_tokens = float("inf")
    
    for name, m in results.items():
        qa = m["qa_accuracy"]
        syntax = m["a2ui_accuracy"]
        tokens = m["total_tokens"]
        
        is_better = False
        if qa > best_qa:
            is_better = True
        elif qa == best_qa:
            if syntax > best_syntax:
                is_better = True
            elif syntax == best_syntax:
                if tokens < best_tokens:
                    is_better = True
                    
        if is_better:
            best_candidate = name
            best_qa = qa
            best_syntax = syntax
            best_tokens = tokens
            
    print("\n" + "="*60)
    print(f"BEST CANDIDATE SELECTED: {best_candidate}")
    print(f"  QA Score: {best_qa:.3f}")
    print(f"  Syntax Score: {best_syntax:.3f}")
    print(f"  Total Tokens: {best_tokens:,}")
    print("="*60)
    
    # Merge best candidate
    best_branch = f"express_mut_{best_candidate}"
    print(f"Merging branch '{best_branch}' into 'a2ui_express_iterate'...")
    subprocess.run(["git", "checkout", "a2ui_express_iterate"], check=True)
    subprocess.run(["git", "merge", best_branch, "--no-edit"], check=True)
    
    # Clean up other branches
    for cand in candidates:
        c_name = cand.get("name")
        branch_name = f"express_mut_{c_name}"
        if c_name != best_candidate:
            print(f"Deleting candidate branch '{branch_name}'...")
            subprocess.run(["git", "branch", "-D", branch_name], stderr=subprocess.DEVNULL)
            
    print("Optimization loop step complete! Baseline updated with the best candidate changes.")

def main():
    parser = argparse.ArgumentParser(description="A2UI Express Optimization Loop CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Extract failures from the latest evaluation run")
    analyze_parser.add_argument("--log-dir", type=str, help="Subdirectory name inside eval/logs to search")
    
    # Mutate command
    subparsers.add_parser("mutate", help="Generate mutation candidates using Gemini and create local branches")
    
    # Evaluate command
    subparsers.add_parser("evaluate", help="Checkout each candidate and run evaluations sequentially")
    
    # Select best command
    subparsers.add_parser("select-best", help="Merge the best performing mutation candidate")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        latest = find_latest_eval_file(args.log_dir)
        if not latest:
            print("No evaluation logs found.")
            sys.exit(1)
        analyze_failures(latest)
    elif args.command == "mutate":
        candidates = generate_mutations()
        if not candidates:
            sys.exit(0)
        for i in range(len(candidates)):
            apply_mutation_to_branch(i)
        print_orchestration_plan(candidates)
    elif args.command == "evaluate":
        run_evals()
    elif args.command == "select-best":
        select_best()

if __name__ == "__main__":
    main()
