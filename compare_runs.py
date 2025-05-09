#!/usr/bin/env python3
"""
Compare multiple simulation runs with different parameters.

Usage:
    python compare_runs.py [--dir DIRECTORY]

This script runs multiple simulations with different parameters and plots the results,
providing an easy way to see the effects of changing parameters.
"""

import subprocess
import argparse
import os
import sys
import json
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def run_simulation(frames=100, seed=42, rows=4, cols=4, hopmax=8, lam=None, label=None):
    """Run simulation with given parameters and return results."""
    if lam is None:
        lam = [4, 4, 2]

    # Define the simulator script (single source of truth)
    SIM = Path('sim.py')  # We use sim.py as it already has the bug fixes

    # Create a unique directory for this run
    if label is None:
        label = f"{rows}x{cols}_hop{hopmax}_lam{'_'.join(str(l) for l in lam)}"

    result_dir = Path(f"results/{label}")
    result_dir.mkdir(parents=True, exist_ok=True)

    # Prepare command with proper argument handling
    cmd = [sys.executable, SIM,
           "--frames", str(frames),
           "--seed", str(seed),
           "--rows", str(rows),
           "--cols", str(cols),
           "--hopmax", str(hopmax)]

    # Add lam arguments
    for l in lam:
        cmd.extend(["--lam", str(l)])

    # Run the simulation
    # Convert all arguments to strings for printing
    cmd_str = [str(c) for c in cmd]
    print(f"Running: {' '.join(cmd_str)}")
    with open(result_dir / "output.txt", "w") as outfile:
        subprocess.run(cmd, check=True, stdout=outfile)

    # Copy the results using Python's shutil for better portability
    shutil.copy("results/run.jsonl", result_dir / "run.jsonl")
    shutil.copy("results/summary.csv", result_dir / "summary.csv")

    # Also copy plot if it exists
    if Path("results/pdr.png").exists():
        shutil.copy("results/pdr.png", result_dir / "pdr.png")

    # Parse and return results
    summary = pd.read_csv(result_dir / "summary.csv")
    return {
        'label': label,
        'params': {
            'frames': frames,
            'rows': rows,
            'cols': cols,
            'hopmax': hopmax,
            'lam': lam
        },
        'pdr': summary['mean_pdr'].iloc[0],
        'latency': summary['mean_latency'].iloc[0],
        'dir': str(result_dir)
    }

def plot_comparison(results, output_dir="results"):
    """Create comparison plots for all simulation runs."""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Extract data for plotting
    labels = [r['label'] for r in results]
    pdr_values = [r['pdr'] for r in results]
    latency_values = [r['latency'] for r in results]
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot PDR
    ax1.bar(range(len(labels)), pdr_values, width=0.6)
    ax1.set_xticks(range(len(labels)))
    ax1.set_xticklabels(labels, rotation=45, ha='right')
    ax1.set_title('Packet Delivery Ratio Comparison')
    ax1.set_ylabel('PDR')
    
    # Plot Latency 
    ax2.bar(range(len(labels)), latency_values, width=0.6)
    ax2.set_xticks(range(len(labels)))
    ax2.set_xticklabels(labels, rotation=45, ha='right')
    ax2.set_title('Latency Comparison')
    ax2.set_ylabel('Latency (time units)')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/comparison.png", dpi=300)
    print(f"Saved comparison plot to {output_dir}/comparison.png")
    
    # Create PDR vs Latency plot
    plt.figure(figsize=(8, 6))
    plt.scatter(pdr_values, latency_values, s=100)
    
    # Add labels for each point
    for i, label in enumerate(labels):
        plt.annotate(label, (pdr_values[i], latency_values[i]), 
                     xytext=(5, 5), textcoords='offset points')
    
    plt.title('PDR-Latency Tradeoff')
    plt.xlabel('Packet Delivery Ratio')
    plt.ylabel('Latency (time units)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{output_dir}/pdr_latency_tradeoff.png", dpi=300)
    print(f"Saved PDR-Latency tradeoff plot to {output_dir}/pdr_latency_tradeoff.png")
    
    # Create summary table
    summary = pd.DataFrame({
        'Label': labels,
        'PDR': pdr_values,
        'Latency': latency_values
    })
    summary.to_csv(f"{output_dir}/comparison_summary.csv", index=False)
    print(f"Saved summary to {output_dir}/comparison_summary.csv")

def main():
    parser = argparse.ArgumentParser(description="Compare multiple simulation runs")
    parser.add_argument('--dir', default='results', help='Output directory')
    args = parser.parse_args()
    
    # Define simulation scenarios
    scenarios = [
        {'label': 'baseline', 'rows': 4, 'cols': 4, 'hopmax': 8, 'lam': [4, 4, 2]},
        {'label': 'high_load', 'rows': 4, 'cols': 4, 'hopmax': 8, 'lam': [6, 6, 3]},
        {'label': 'low_hop', 'rows': 4, 'cols': 4, 'hopmax': 4, 'lam': [4, 4, 2]},
        {'label': 'large_grid', 'rows': 5, 'cols': 5, 'hopmax': 8, 'lam': [4, 4, 2]}
    ]
    
    results = []
    for scenario in scenarios:
        print(f"\nRunning scenario: {scenario['label']}")
        result = run_simulation(frames=100, seed=42, **scenario)
        results.append(result)
    
    # Create comparison plots
    plot_comparison(results, args.dir)
    
    print("\nAll simulations complete. Results are in the results directory.")

if __name__ == "__main__":
    main()