#!/usr/bin/env python
"""
Script to run all improvement scripts.
This script runs all the improvement scripts in the correct order.
"""

import os
import sys
import subprocess
from pathlib import Path

# Define the scripts to run
SCRIPTS = [
    'standardize_app_structure.py',
    'enforce_import_ordering.py',
    'separate_business_logic.py',
    'convert_to_class_based_views.py',
    'add_docstrings.py',
    'optimize_database_queries.py',
    'implement_error_handling.py',
]

def run_script(script_path):
    """Run a Python script."""
    print(f"Running {script_path}...")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running {script_path}:")
        print(result.stderr)
        return False
    
    print(result.stdout)
    return True

def run_all_improvements():
    """Run all improvement scripts."""
    success = True
    
    for script in SCRIPTS:
        script_path = Path(script)
        
        if not script_path.exists():
            print(f"Script {script} not found.")
            success = False
            continue
        
        if not run_script(script_path):
            success = False
    
    return success

if __name__ == "__main__":
    print("Running all improvement scripts...")
    if run_all_improvements():
        print("All improvements completed successfully!")
    else:
        print("Some improvements failed. Check the output for details.")
        sys.exit(1)
