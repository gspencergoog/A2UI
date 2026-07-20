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

"""Compares A2UI evaluation run results directories against a baseline directory."""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple


def resolve_results_file(target_path: str) -> str:
    """Resolves results.json from a directory, .eval file, or direct json file path."""
    if os.path.isfile(target_path):
        if target_path.endswith(".json"):
            return target_path
        elif target_path.endswith(".eval"):
            uv_bin = shutil.which("uv") or "/usr/local/google/home/gspencer/.local/bin/uv"
            dump_cmd = [uv_bin, "run", "inspect", "log", "dump", target_path]
            data = json.loads(subprocess.check_output(dump_cmd, text=True))
            temp_json = target_path + ".json"
            with open(temp_json, "w", encoding="utf-8") as f:
                json.dump(data, f)
            return temp_json

    if os.path.isdir(target_path):
        res_json = os.path.join(target_path, "results.json")
        if os.path.exists(res_json):
            return res_json
        
        # Search for .eval files inside directory
        eval_files = glob.glob(os.path.join(target_path, "*.eval")) + glob.glob(os.path.join(target_path, "**/*.eval"), recursive=True)
        if eval_files:
            uv_bin = shutil.which("uv") or "/usr/local/google/home/gspencer/.local/bin/uv"
            dump_cmd = [uv_bin, "run", "inspect", "log", "dump", eval_files[0]]
            data = json.loads(subprocess.check_output(dump_cmd, text=True))
            temp_json = os.path.join(target_path, "results.json")
            with open(temp_json, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return temp_json

    raise FileNotFoundError(f"Could not find valid results.json or .eval file in: '{target_path}'")


def extract_metrics(json_path: str, label_name: str = "") -> Dict[str, Any]:
    """Extracts summary and per-sample metadata metrics from results JSON data."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract name/label
    name = label_name or os.path.basename(os.path.dirname(json_path))
    if not name or name in (".", ".."):
        name = os.path.basename(json_path)

    eval_spec = data.get("eval", {})
    task_name = eval_spec.get("task", "unknown")

    # Scorer metrics
    scores = data.get("results", {}).get("scores", [])
    schema_acc = None
    quality_acc = None

    for s in scores:
        s_name = s.get("name") or s.get("scorer", "")
        metrics = s.get("metrics", {})
        acc_val = metrics.get("accuracy", {}).get("value")
        if acc_val is not None:
            if s_name == "a2ui_scorer":
                schema_acc = float(acc_val)
            elif s_name == "measured_model_graded_qa":
                quality_acc = float(acc_val)
            elif schema_acc is None:
                schema_acc = float(acc_val)

    samples = data.get("samples", [])
    sample_count = len(samples) if samples else data.get("results", {}).get("total_samples", 0)

    # Metadata aggregation
    durations = []
    input_tokens = []
    output_tokens = []
    cached_tokens = []

    for sample in samples:
        meta = sample.get("metadata", {})
        
        # Redefined inference_duration_seconds: extract pure model working_time excluding retries
        sample_duration = None
        events = sample.get("events", [])
        model_events = [e for e in events if e.get("event") == "model"]
        if model_events:
            m = model_events[0]
            sample_duration = m.get("working_time") or m.get("time") or (m.get("call", {}).get("time") if isinstance(m.get("call"), dict) else None)

        if sample_duration is None and "inference_duration_seconds" in meta:
            sample_duration = meta["inference_duration_seconds"]

        if sample_duration is not None:
            durations.append(sample_duration)

        if "inference_input_tokens" in meta:
            input_tokens.append(meta["inference_input_tokens"])
        if "inference_output_tokens" in meta:
            output_tokens.append(meta["inference_output_tokens"])
        if "inference_cached_tokens" in meta:
            cached_tokens.append(meta["inference_cached_tokens"])

    # Wall-clock duration calculation from stats
    stats = data.get("stats", {})
    started_at_str = stats.get("started_at")
    completed_at_str = stats.get("completed_at")
    wall_clock_duration = 0.0
    if started_at_str and completed_at_str:
        try:
            from datetime import datetime
            t_start = datetime.fromisoformat(started_at_str)
            t_end = datetime.fromisoformat(completed_at_str)
            wall_clock_duration = (t_end - t_start).total_seconds()
        except Exception:
            wall_clock_duration = 0.0

    wall_clock_per_sample = wall_clock_duration / max(sample_count, 1) if wall_clock_duration > 0 else 0.0

    # Fallback stats model usage if sample metadata is empty
    model_usage = data.get("stats", {}).get("model_usage", {})
    primary_usage = next(iter(model_usage.values()), {}) if model_usage else {}

    avg_duration = sum(durations) / max(len(durations), 1) if durations else 0.0
    avg_input_tokens = sum(input_tokens) / max(len(input_tokens), 1) if input_tokens else (primary_usage.get("input_tokens", 0) / max(sample_count, 1))
    avg_output_tokens = sum(output_tokens) / max(len(output_tokens), 1) if output_tokens else (primary_usage.get("output_tokens", 0) / max(sample_count, 1))
    avg_cached_tokens = sum(cached_tokens) / max(len(cached_tokens), 1) if cached_tokens else (primary_usage.get("input_tokens_cache_read", 0) / max(sample_count, 1))

    total_duration = sum(durations)
    total_input_tokens = sum(input_tokens) if input_tokens else primary_usage.get("input_tokens", 0)
    total_output_tokens = sum(output_tokens) if output_tokens else primary_usage.get("output_tokens", 0)

    return {
        "name": name,
        "path": json_path,
        "sample_count": sample_count,
        "schema_acc": schema_acc,
        "quality_acc": quality_acc,
        "avg_duration": avg_duration,
        "wall_clock_duration": wall_clock_duration,
        "wall_clock_per_sample": wall_clock_per_sample,
        "avg_input_tokens": avg_input_tokens,
        "avg_output_tokens": avg_output_tokens,
        "avg_cached_tokens": avg_cached_tokens,
        "total_duration": total_duration,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
    }


def format_delta_pct(val: float, base_val: float, is_percentage_points: bool = False) -> str:
    """Formats percentage change or point diff against baseline."""
    if base_val == 0.0 or base_val is None or val is None:
        return "-"
    
    if is_percentage_points:
        diff = (val - base_val) * 100
        sign = "+" if diff > 0 else ""
        return f"{sign}{diff:.1f}%"
    
    pct_change = ((val - base_val) / base_val) * 100
    sign = "+" if pct_change > 0 else ""
    return f"{sign}{pct_change:.1f}%"


def generate_markdown_table(
    baseline_metrics: Dict[str, Any],
    comparison_metrics_list: List[Dict[str, Any]],
) -> str:
    """Renders a GFM comparison markdown table."""
    lines = []
    lines.append("### A2UI Evaluation Comparison & Baseline Delta")
    lines.append("")

    headers = [
        "Run / Results Directory",
        "Samples",
        "Schema Acc (Delta)",
        "Quality Score (Delta)",
        "Wall Latency (Delta)",
        "Sample Latency (Delta)",
        "Avg Input Tokens (Delta)",
        "Avg Output Tokens (Delta)",
    ]

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join([":---" if i == 0 else ":---:" for i in range(len(headers))]) + " |")

    # Format baseline row
    b = baseline_metrics
    b_schema_str = f"{b['schema_acc']*100:.1f}%" if b['schema_acc'] is not None else "N/A"
    b_quality_str = f"{b['quality_acc']*100:.1f}%" if b['quality_acc'] is not None else "N/A"
    b_wall_str = f"{b['wall_clock_per_sample']:.2f}s" if b['wall_clock_per_sample'] > 0 else "N/A"
    b_lat_str = f"{b['avg_duration']:.2f}s"
    b_inp_str = f"{b['avg_input_tokens']:,.0f}"
    b_out_str = f"{b['avg_output_tokens']:,.0f}"

    lines.append(
        f"| **Baseline**: `{b['name']}` | {b['sample_count']} | {b_schema_str} | {b_quality_str} | {b_wall_str} | {b_lat_str} | {b_inp_str} | {b_out_str} |"
    )

    # Format comparison rows
    for c in comparison_metrics_list:
        name_str = f"`{c['name']}`"
        samples_str = str(c["sample_count"])

        # Schema Acc
        if c["schema_acc"] is not None:
            c_schema_val = f"{c['schema_acc']*100:.1f}%"
            d_schema = format_delta_pct(c["schema_acc"], b["schema_acc"], is_percentage_points=True)
            schema_cell = f"{c_schema_val} ({d_schema})"
        else:
            schema_cell = "N/A"

        # Quality Acc
        if c["quality_acc"] is not None:
            c_qual_val = f"{c['quality_acc']*100:.1f}%"
            d_qual = format_delta_pct(c["quality_acc"], b["quality_acc"], is_percentage_points=True)
            quality_cell = f"{c_qual_val} ({d_qual})"
        else:
            quality_cell = "N/A"

        # Wall Latency
        if c["wall_clock_per_sample"] > 0:
            c_wall_val = f"{c['wall_clock_per_sample']:.2f}s"
            d_wall = format_delta_pct(c["wall_clock_per_sample"], b["wall_clock_per_sample"])
            wall_cell = f"{c_wall_val} ({d_wall})"
        else:
            wall_cell = "N/A"

        # Sample Latency
        c_lat_val = f"{c['avg_duration']:.2f}s"
        d_lat = format_delta_pct(c["avg_duration"], b["avg_duration"])
        latency_cell = f"{c_lat_val} ({d_lat})"

        # Input Tokens
        c_inp_val = f"{c['avg_input_tokens']:,.0f}"
        d_inp = format_delta_pct(c["avg_input_tokens"], b["avg_input_tokens"])
        inp_cell = f"{c_inp_val} ({d_inp})"

        # Output Tokens
        c_out_val = f"{c['avg_output_tokens']:,.0f}"
        d_out = format_delta_pct(c["avg_output_tokens"], b["avg_output_tokens"])
        out_cell = f"{c_out_val} ({d_out})"

        lines.append(
            f"| {name_str} | {samples_str} | {schema_cell} | {quality_cell} | {wall_cell} | {latency_cell} | {inp_cell} | {out_cell} |"
        )

    lines.append("")
    lines.append("*Notes: Latency and token metrics represent per-sample averages. Delta percentages indicate relative gain (+) or reduction (-) against the baseline.*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare A2UI evaluation results against a baseline directory."
    )
    parser.add_argument(
        "--baseline",
        type=str,
        required=True,
        help="Path to baseline results directory or results.json file",
    )
    parser.add_argument(
        "results_dirs",
        nargs="+",
        help="One or more target results directories or json files to compare against baseline",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output markdown file path to save report",
    )

    args = parser.parse_args()

    # Load baseline
    baseline_json = resolve_results_file(args.baseline)
    baseline_metrics = extract_metrics(baseline_json, label_name=os.path.basename(os.path.normpath(args.baseline)))

    # Load comparison runs
    comp_metrics_list = []
    for r_dir in args.results_dirs:
        res_json = resolve_results_file(r_dir)
        label = os.path.basename(os.path.normpath(r_dir))
        m = extract_metrics(res_json, label_name=label)
        comp_metrics_list.append(m)

    table_md = generate_markdown_table(baseline_metrics, comp_metrics_list)
    print(table_md)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(table_md)
        print(f"\nSaved comparison table to: {args.output}")


if __name__ == "__main__":
    main()
