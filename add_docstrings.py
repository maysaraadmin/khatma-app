#!/usr/bin/env python
"""
Script to add proper docstrings to all Python files.
This script ensures all modules, classes, and functions have proper docstrings.
"""

import os
import re
import ast
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

class DocstringVisitor(ast.NodeVisitor):
    """AST visitor to add docstrings."""
    
    def __init__(self):
        self.changes = []
    
    def visit_Module(self, node):
        """Visit module node."""
        # Check if module has a docstring
        if not node.body or not isinstance(node.body[0], ast.Expr) or not isinstance(node.body[0].value, ast.Str):
            # Add module docstring
            module_name = "Module"
            docstring = f'"""This module contains {module_name} functionality."""'
            self.changes.append((node, 0, ast.Expr(ast.Str(s=docstring))))
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definition."""
        # Check if class has a docstring
        if not node.body or not isinstance(node.body[0], ast.Expr) or not isinstance(node.body[0].value, ast.Str):
            # Add class docstring
            docstring = f'"""Class representing {node.name}."""'
            self.changes.append((node, 0, ast.Expr(ast.Str(s=docstring))))
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        # Check if function has a docstring
        if not node.body or not isinstance(node.body[0], ast.Expr) or not isinstance(node.body[0].value, ast.Str):
            # Add function docstring
            docstring = f'"""Function to {node.name.replace("_", " ")}."""'
            self.changes.append((node, 0, ast.Expr(ast.Str(s=docstring))))
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition."""
        # Check if async function has a docstring
        if not node.body or not isinstance(node.body[0], ast.Expr) or not isinstance(node.body[0].value, ast.Str):
            # Add async function docstring
            docstring = f'"""Async function to {node.name.replace("_", " ")}."""'
            self.changes.append((node, 0, ast.Expr(ast.Str(s=docstring))))
        
        self.generic_visit(node)

def add_docstrings_to_file(file_path):
    """Add docstrings to a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the file
    try:
        tree = ast.parse(content)
    except SyntaxError:
        print(f"  Skipping file with syntax error: {file_path}")
        return
    
    # Add docstrings
    visitor = DocstringVisitor()
    visitor.visit(tree)
    
    # Apply changes
    if visitor.changes:
        print(f"  Adding {len(visitor.changes)} docstrings to {file_path}")
        
        # Sort changes in reverse order to avoid affecting earlier positions
        visitor.changes.sort(key=lambda x: (id(x[0]), -x[1]))
        
        for node, index, docstring in visitor.changes:
            node.body.insert(index, docstring)
        
        # Generate code from modified tree
        new_content = ast.unparse(tree)
        
        # Write new content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

def add_docstrings():
    """Add docstrings to all Python files."""
    for app_name in APPS:
        print(f"Adding docstrings to {app_name} app...")
        app_dir = PROJECT_ROOT / app_name
        
        # Skip if app directory doesn't exist
        if not app_dir.exists():
            print(f"  Skipping non-existent app: {app_name}")
            continue
        
        # Process Python files in app directory
        for file_path in app_dir.glob('**/*.py'):
            add_docstrings_to_file(file_path)

if __name__ == "__main__":
    print("Adding docstrings to Python files...")
    add_docstrings()
    print("Done!")
