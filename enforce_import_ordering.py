#!/usr/bin/env python
"""
Script to enforce consistent import ordering across the project.
This script ensures all Python files follow the same import order:
1. Standard library imports
2. Django imports
3. Third-party app imports
4. Local app imports
"""

import os
import re
import ast
from pathlib import Path
from collections import defaultdict

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

# Define import categories
STANDARD_LIBS = set([
    'abc', 'argparse', 'asyncio', 'collections', 'contextlib', 'copy', 'csv', 'datetime',
    'decimal', 'enum', 'functools', 'glob', 'hashlib', 'importlib', 'inspect', 'io',
    'itertools', 'json', 'logging', 'math', 'os', 'pathlib', 'pickle', 'random',
    're', 'shutil', 'signal', 'socket', 'string', 'subprocess', 'sys', 'tempfile',
    'time', 'traceback', 'typing', 'uuid', 'warnings', 'zipfile'
])

DJANGO_MODULES = set([
    'django', 'rest_framework', 'corsheaders', 'drf_yasg'
])

THIRD_PARTY_MODULES = set([
    'allauth', 'celery', 'crispy_forms', 'debug_toolbar', 'environ', 'gunicorn',
    'markdown', 'pillow', 'psycopg2', 'pytest', 'requests', 'sentry_sdk',
    'whitenoise', 'storages'
])

class ImportOrganizer(ast.NodeVisitor):
    """AST visitor to organize imports."""
    
    def __init__(self):
        self.imports = defaultdict(list)
        self.import_froms = defaultdict(list)
        self.docstring = None
        self.future_imports = []
        self.other_nodes = []
    
    def visit_Module(self, node):
        """Visit module node."""
        # Extract docstring if present
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            self.docstring = node.body[0]
            node.body = node.body[1:]
        
        # Visit all nodes
        for n in node.body:
            if isinstance(n, ast.Import):
                self.visit_Import(n)
            elif isinstance(n, ast.ImportFrom):
                self.visit_ImportFrom(n)
            else:
                self.other_nodes.append(n)
    
    def visit_Import(self, node):
        """Visit import node."""
        for name in node.names:
            module = name.name.split('.')[0]
            if module in STANDARD_LIBS:
                self.imports['standard'].append(node)
            elif module in DJANGO_MODULES:
                self.imports['django'].append(node)
            elif module in THIRD_PARTY_MODULES:
                self.imports['third_party'].append(node)
            elif module in APPS:
                self.imports['local'].append(node)
            else:
                self.imports['unknown'].append(node)
    
    def visit_ImportFrom(self, node):
        """Visit import from node."""
        if node.module is None:  # relative import
            self.import_froms['local'].append(node)
            return
        
        module = node.module.split('.')[0]
        if module == '__future__':
            self.future_imports.append(node)
        elif module in STANDARD_LIBS:
            self.import_froms['standard'].append(node)
        elif module in DJANGO_MODULES:
            self.import_froms['django'].append(node)
        elif module in THIRD_PARTY_MODULES:
            self.import_froms['third_party'].append(node)
        elif module in APPS:
            self.import_froms['local'].append(node)
        else:
            self.import_froms['unknown'].append(node)
    
    def get_organized_imports(self):
        """Get organized imports."""
        organized_imports = []
        
        # Add future imports first
        if self.future_imports:
            organized_imports.extend(self.future_imports)
            organized_imports.append(ast.Expr(ast.Str('\n')))
        
        # Add imports by category
        categories = ['standard', 'django', 'third_party', 'local', 'unknown']
        for category in categories:
            if self.imports[category] or self.import_froms[category]:
                if organized_imports:
                    organized_imports.append(ast.Expr(ast.Str('\n')))
                
                # Add regular imports
                organized_imports.extend(self.imports[category])
                
                # Add import from statements
                organized_imports.extend(self.import_froms[category])
        
        return organized_imports

def organize_imports_in_file(file_path):
    """Organize imports in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the file
    try:
        tree = ast.parse(content)
    except SyntaxError:
        print(f"  Skipping file with syntax error: {file_path}")
        return
    
    # Organize imports
    organizer = ImportOrganizer()
    organizer.visit(tree)
    
    # Create new tree with organized imports
    new_body = []
    
    # Add docstring
    if organizer.docstring:
        new_body.append(organizer.docstring)
    
    # Add organized imports
    new_body.extend(organizer.get_organized_imports())
    
    # Add other nodes
    new_body.extend(organizer.other_nodes)
    
    # Create new tree
    new_tree = ast.Module(body=new_body, type_ignores=[])
    
    # Generate code from new tree
    new_content = ast.unparse(new_tree)
    
    # Write new content to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def enforce_import_ordering():
    """Enforce consistent import ordering across the project."""
    for app_name in APPS:
        print(f"Enforcing import ordering for {app_name} app...")
        app_dir = PROJECT_ROOT / app_name
        
        # Skip if app directory doesn't exist
        if not app_dir.exists():
            print(f"  Skipping non-existent app: {app_name}")
            continue
        
        # Process Python files in app directory
        for file_path in app_dir.glob('**/*.py'):
            print(f"  Processing file: {file_path.relative_to(PROJECT_ROOT)}")
            organize_imports_in_file(file_path)

if __name__ == "__main__":
    print("Enforcing import ordering...")
    enforce_import_ordering()
    print("Done!")
