#!/usr/bin/env python
"""
Script to check code quality.
This script runs various code quality checks and generates a report.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from collections import defaultdict

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

def run_pylint():
    """Run pylint on the project."""
    print("Running pylint...")
    
    results = {}
    
    for app_name in APPS:
        app_dir = PROJECT_ROOT / app_name
        
        # Skip if app directory doesn't exist
        if not app_dir.exists():
            print(f"  Skipping non-existent app: {app_name}")
            continue
        
        # Run pylint on app directory
        result = subprocess.run(
            ['pylint', app_name, '--output-format=json'],
            capture_output=True,
            text=True
        )
        
        # Parse pylint output
        try:
            pylint_results = json.loads(result.stdout)
            results[app_name] = pylint_results
        except json.JSONDecodeError:
            print(f"  Error parsing pylint output for {app_name}")
            results[app_name] = []
    
    return results

def run_flake8():
    """Run flake8 on the project."""
    print("Running flake8...")
    
    results = defaultdict(list)
    
    for app_name in APPS:
        app_dir = PROJECT_ROOT / app_name
        
        # Skip if app directory doesn't exist
        if not app_dir.exists():
            print(f"  Skipping non-existent app: {app_name}")
            continue
        
        # Run flake8 on app directory
        result = subprocess.run(
            ['flake8', app_name, '--format=json'],
            capture_output=True,
            text=True
        )
        
        # Parse flake8 output
        try:
            flake8_results = json.loads(result.stdout)
            for item in flake8_results:
                results[app_name].append(item)
        except json.JSONDecodeError:
            print(f"  Error parsing flake8 output for {app_name}")
    
    return results

def run_bandit():
    """Run bandit on the project."""
    print("Running bandit...")
    
    results = {}
    
    for app_name in APPS:
        app_dir = PROJECT_ROOT / app_name
        
        # Skip if app directory doesn't exist
        if not app_dir.exists():
            print(f"  Skipping non-existent app: {app_name}")
            continue
        
        # Run bandit on app directory
        result = subprocess.run(
            ['bandit', '-r', app_name, '-f', 'json'],
            capture_output=True,
            text=True
        )
        
        # Parse bandit output
        try:
            bandit_results = json.loads(result.stdout)
            results[app_name] = bandit_results
        except json.JSONDecodeError:
            print(f"  Error parsing bandit output for {app_name}")
            results[app_name] = {}
    
    return results

def generate_report(pylint_results, flake8_results, bandit_results):
    """Generate a code quality report."""
    print("Generating code quality report...")
    
    report = {
        'pylint': pylint_results,
        'flake8': flake8_results,
        'bandit': bandit_results
    }
    
    # Write report to file
    with open('code_quality_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Generate summary
    summary = {
        'pylint': {},
        'flake8': {},
        'bandit': {}
    }
    
    # Pylint summary
    for app_name, results in pylint_results.items():
        summary['pylint'][app_name] = len(results)
    
    # Flake8 summary
    for app_name, results in flake8_results.items():
        summary['flake8'][app_name] = len(results)
    
    # Bandit summary
    for app_name, results in bandit_results.items():
        if 'results' in results:
            summary['bandit'][app_name] = len(results['results'])
        else:
            summary['bandit'][app_name] = 0
    
    # Write summary to file
    with open('code_quality_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    return summary

def check_code_quality():
    """Check code quality and generate a report."""
    # Install required packages
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pylint', 'flake8', 'bandit'])
    
    # Run code quality checks
    pylint_results = run_pylint()
    flake8_results = run_flake8()
    bandit_results = run_bandit()
    
    # Generate report
    summary = generate_report(pylint_results, flake8_results, bandit_results)
    
    # Print summary
    print("\nCode Quality Summary:")
    print("=====================")
    
    print("\nPylint Issues:")
    for app_name, count in summary['pylint'].items():
        print(f"  {app_name}: {count} issues")
    
    print("\nFlake8 Issues:")
    for app_name, count in summary['flake8'].items():
        print(f"  {app_name}: {count} issues")
    
    print("\nBandit Issues:")
    for app_name, count in summary['bandit'].items():
        print(f"  {app_name}: {count} issues")
    
    print("\nDetailed reports saved to code_quality_report.json and code_quality_summary.json")

if __name__ == "__main__":
    print("Checking code quality...")
    check_code_quality()
    print("Done!")
