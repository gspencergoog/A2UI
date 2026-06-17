import zipfile
import json
import numpy as np
import os

DIRECT_EVAL = "/Users/gspencer/code/a2ui/a2ui_express/eval/logs/latency_comparison_3_5/2026-06-17T01-52-06-00-00_a2ui-v0-9-1-eval_SYgJKCy4dZ8SdiH3CKw9Jm.eval"
EXPRESS_EVAL = "/Users/gspencer/code/a2ui/a2ui_express/eval/logs/latency_comparison_3_5/2026-06-17T01-52-06-00-00_a2ui-v0-9-1-eval_mFBuzz4Jvd2Su97iZVSf7Z.eval"

def analyze_latency(eval_path, name):
    print(f"Checking {name} path: {eval_path}")
    if not os.path.exists(eval_path):
        print(f"Error: {eval_path} not found.")
        return None
        
    latencies = []
    output_tokens = []
    total_tokens = []
    
    with zipfile.ZipFile(eval_path, "r") as z:
        sample_files = [n for n in z.namelist() if n.startswith("samples/") and n.endswith(".json")]
        print(f"Found {len(sample_files)} sample files in {name}")
        
        for sf in sample_files:
            try:
                sample = json.loads(z.read(sf))
                events = sample.get("events", [])
                
                # Preferentially read duration from metadata (which isolates solver active time)
                metadata = sample.get("metadata", {})
                sample_duration = metadata.get("inference_duration_seconds")
                sample_out_tokens = metadata.get("inference_output_tokens")
                sample_total_tokens = None
                
                # If not present in metadata, fallback to parsing events
                if sample_duration is None:
                    sample_duration = 0.0
                    sample_out_tokens = 0
                    sample_total_tokens = 0
                    for e in events:
                        if e.get("event") == "model" and "gemini-3.5-flash" in e.get("model", ""):
                            # Skip grader model calls if they happen to share the same model name
                            # The grader event prompt usually contains grading rubrics
                            call_data = e.get("call", {})
                            req = call_data.get("request", {})
                            sys_inst = str(req.get("system_instruction", ""))
                            if "rubric" in sys_inst.lower() or "grader" in sys_inst.lower() or "grading" in sys_inst.lower():
                                continue
                                
                            sample_duration += e.get("working_time", 0.0)
                            out_tok = 0
                            tot_tok = 0
                            usage = e.get("output", {}).get("usage")
                            if isinstance(usage, dict):
                                out_tok = usage.get("output_tokens", 0)
                                tot_tok = usage.get("total_tokens", 0)
                            else:
                                meta = e.get("output", {}).get("usageMetadata", {})
                                if isinstance(meta, dict):
                                    out_tok = meta.get("candidatesTokenCount", 0)
                                    tot_tok = meta.get("totalTokenCount", 0)
                            sample_out_tokens += out_tok
                            sample_total_tokens += tot_tok
                else:
                    # Resolve total tokens for metadata path
                    inf_input = metadata.get("inference_input_tokens", 0)
                    sample_total_tokens = inf_input + (sample_out_tokens or 0)
                            
                if sample_duration is not None and sample_duration > 0:
                    latencies.append(sample_duration)
                if sample_out_tokens is not None and sample_out_tokens > 0:
                    output_tokens.append(sample_out_tokens)
                if sample_total_tokens is not None and sample_total_tokens > 0:
                    total_tokens.append(sample_total_tokens)
            except Exception as e:
                print(f"Error reading {sf} in {name}: {e}")
                
    print(f"Parsed {len(latencies)} durations for {name}")
    if not latencies:
        return None
        
    return {
        "name": name,
        "mean_latency": np.mean(latencies),
        "median_latency": np.median(latencies),
        "p90_latency": np.percentile(latencies, 90),
        "mean_out_tokens": np.mean(output_tokens) if output_tokens else 0,
        "mean_total_tokens": np.mean(total_tokens) if total_tokens else 0,
        "throughput_tps": np.sum(output_tokens) / np.sum(latencies) if output_tokens and latencies else 0,
        "sample_count": len(latencies)
    }

import sys

def main():
    print("Analyzing and comparing generation latency...")
    
    express_path = EXPRESS_EVAL
    express_label = "A2UI Express DSL"
    
    if len(sys.argv) > 1:
        arg_path = sys.argv[1]
        if os.path.isdir(arg_path):
            # Find the .eval file inside the folder
            import glob
            eval_files = glob.glob(os.path.join(arg_path, "*.eval"))
            if eval_files:
                express_path = eval_files[0]
            else:
                express_path = arg_path
        else:
            express_path = arg_path
        express_label = "A2UI Express (JSON Tree)"
        
    direct_metrics = analyze_latency(DIRECT_EVAL, "Direct JSON (Non-Express)")
    express_metrics = analyze_latency(express_path, express_label)
    
    if not direct_metrics or not express_metrics:
        print("Could not complete analysis.")
        return
        
    print("\n" + "="*80)
    print("LATENCY & TOKEN PERFORMANCE COMPARISON TABLE")
    print("="*80)
    print(f"{'Metric':<30} | {'Direct JSON':<20} | {'A2UI Express':<20} | {'Improvement':<12}")
    print("-" * 90)
    
    mean_lat_diff = (direct_metrics["mean_latency"] - express_metrics["mean_latency"]) / direct_metrics["mean_latency"] * 100
    median_lat_diff = (direct_metrics["median_latency"] - express_metrics["median_latency"]) / direct_metrics["median_latency"] * 100
    out_tok_diff = (direct_metrics["mean_out_tokens"] - express_metrics["mean_out_tokens"]) / direct_metrics["mean_out_tokens"] * 100
    
    print(f"{'Mean Latency (s)':<30} | {direct_metrics['mean_latency']:<20.3f} | {express_metrics['mean_latency']:<20.3f} | {mean_lat_diff:<10.1f}%")
    print(f"{'Median Latency (s)':<30} | {direct_metrics['median_latency']:<20.3f} | {express_metrics['median_latency']:<20.3f} | {median_lat_diff:<10.1f}%")
    print(f"{'90th Percentile Latency (s)':<30} | {direct_metrics['p90_latency']:<20.3f} | {express_metrics['p90_latency']:<20.3f} | {((direct_metrics['p90_latency'] - express_metrics['p90_latency'])/direct_metrics['p90_latency']*100):<10.1f}%")
    print(f"{'Mean Output Tokens':<30} | {direct_metrics['mean_out_tokens']:<20.1f} | {express_metrics['mean_out_tokens']:<20.1f} | {out_tok_diff:<10.1f}%")
    print(f"{'Throughput (Tokens/sec)':<30} | {direct_metrics['throughput_tps']:<20.2f} | {express_metrics['throughput_tps']:<20.2f} | {((express_metrics['throughput_tps'] - direct_metrics['throughput_tps'])/direct_metrics['throughput_tps']*100):<10.1f}%")
    print(f"{'Dataset Sample Count':<30} | {direct_metrics['sample_count']:<20} | {express_metrics['sample_count']:<20} | -")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
