#!/usr/bin/env python
"""
Script to organize the app and make it follow best practices.
This script runs all the improvement scripts in the correct order.
"""

import os
import sys
import subprocess
import argparse
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
    'check_code_quality.py',
    'generate_documentation.py',
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

def organize_app(args):
    """Organize the app and make it follow best practices."""
    success = True
    
    # Run selected scripts
    for script in SCRIPTS:
        # Skip scripts based on arguments
        if script == 'standardize_app_structure.py' and not args.structure:
            continue
        elif script == 'enforce_import_ordering.py' and not args.imports:
            continue
        elif script == 'separate_business_logic.py' and not args.logic:
            continue
        elif script == 'convert_to_class_based_views.py' and not args.views:
            continue
        elif script == 'add_docstrings.py' and not args.docs:
            continue
        elif script == 'optimize_database_queries.py' and not args.queries:
            continue
        elif script == 'implement_error_handling.py' and not args.errors:
            continue
        elif script == 'check_code_quality.py' and not args.quality:
            continue
        elif script == 'generate_documentation.py' and not args.documentation:
            continue
        
        script_path = Path(script)
        
        if not script_path.exists():
            print(f"Script {script} not found.")
            success = False
            continue
        
        if not run_script(script_path):
            success = False
    
    return success

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Organize the app and make it follow best practices.')
    parser.add_argument('--all', action='store_true', help='Run all scripts')
    parser.add_argument('--structure', action='store_true', help='Standardize app structure')
    parser.add_argument('--imports', action='store_true', help='Enforce import ordering')
    parser.add_argument('--logic', action='store_true', help='Separate business logic')
    parser.add_argument('--views', action='store_true', help='Convert to class-based views')
    parser.add_argument('--docs', action='store_true', help='Add docstrings')
    parser.add_argument('--queries', action='store_true', help='Optimize database queries')
    parser.add_argument('--errors', action='store_true', help='Implement error handling')
    parser.add_argument('--quality', action='store_true', help='Check code quality')
    parser.add_argument('--documentation', action='store_true', help='Generate documentation')
    args = parser.parse_args()
    
    # If no arguments are provided, run all scripts
    if not any(vars(args).values()):
        args.all = True
    
    # If --all is specified, run all scripts
    if args.all:
        args.structure = True
        args.imports = True
        args.logic = True
        args.views = True
        args.docs = True
        args.queries = True
        args.errors = True
        args.quality = True
        args.documentation = True
    
    print("Organizing app and making it follow best practices...")
    if organize_app(args):
        print("App organization completed successfully!")
    else:
        print("App organization failed. Check the output for details.")
        sys.exit(1)
