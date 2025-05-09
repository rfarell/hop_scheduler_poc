#!/usr/bin/env python3
"""
Aggregates all key files in the hop-budget-aware scheduler repo into a single text file.
This makes it easier to share the entire codebase with Gemini or other LLMs.
"""

import os
from pathlib import Path

def read_file(file_path):
    """Read a file and return its contents with a header showing the file name."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    header = f"\n\n{'='*80}\n{file_path}\n{'='*80}\n"
    return header + content

def main():
    # Define the important files to include
    key_files = [
        'README.md',
        'scheduler.py',
        'sim.py',
        'topology.py',
        'traffic.py',
        'plot.py',
        'compare_runs.py',
        '__init__.py',
        'requirements.txt'
    ]
    
    # Create the aggregated file
    output_path = Path('aggregated_code.txt')
    
    with open(output_path, 'w') as outfile:
        outfile.write("# AGGREGATED HOP-BUDGET-AWARE SCHEDULER CODE\n")
        outfile.write("This file contains all key components of the scheduler simulation project\n\n")
        
        for file in key_files:
            try:
                content = read_file(file)
                outfile.write(content)
            except FileNotFoundError:
                outfile.write(f"\n\n{'='*80}\n{file} (FILE NOT FOUND)\n{'='*80}\n")
    
    print(f"Created aggregated file at {output_path.absolute()}")
    
    # Print file size
    size_kb = output_path.stat().st_size / 1024
    print(f"File size: {size_kb:.2f} KB")

if __name__ == "__main__":
    main()