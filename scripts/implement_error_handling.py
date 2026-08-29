#!/usr/bin/env python
"""
Script to implement proper error handling.
This script adds try-except blocks to view functions and adds logging.
"""

import os
import re
import ast
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

class ErrorHandlingVisitor(ast.NodeVisitor):
    """AST visitor to add error handling."""
    
    def __init__(self):
        self.changes = []
        self.current_function = None
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        # Save current function
        old_function = self.current_function
        self.current_function = node
        
        # Check if this is a view function
        is_view = False
        if node.args.args and len(node.args.args) > 0:
            first_arg = node.args.args[0]
            if first_arg.arg == 'request':
                is_view = True
        
        if is_view and not self.has_try_except(node):
            # Add try-except block
            self.add_try_except(node)
        
        # Visit children
        self.generic_visit(node)
        
        # Restore current function
        self.current_function = old_function
    
    def has_try_except(self, node):
        """Check if a function already has a try-except block."""
        for stmt in node.body:
            if isinstance(stmt, ast.Try):
                return True
        return False
    
    def add_try_except(self, node):
        """Add a try-except block to a function."""
        # Create try-except block
        try_except = ast.Try(
            body=node.body,
            handlers=[
                ast.ExceptHandler(
                    type=ast.Name(id='Exception', ctx=ast.Load()),
                    name='e',
                    body=[
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id='logging', ctx=ast.Load()),
                                    attr='error',
                                    ctx=ast.Load()
                                ),
                                args=[
                                    ast.BinOp(
                                        left=ast.Str(s=f"Error in {node.name}: "),
                                        op=ast.Add(),
                                        right=ast.Call(
                                            func=ast.Name(id='str', ctx=ast.Load()),
                                            args=[ast.Name(id='e', ctx=ast.Load())],
                                            keywords=[]
                                        )
                                    )
                                ],
                                keywords=[]
                            )
                        ),
                        ast.Return(
                            value=ast.Call(
                                func=ast.Name(id='render', ctx=ast.Load()),
                                args=[
                                    ast.Name(id='request', ctx=ast.Load()),
                                    ast.Str(s='core/error.html')
                                ],
                                keywords=[
                                    ast.keyword(
                                        arg='context',
                                        value=ast.Dict(
                                            keys=[ast.Str(s='error')],
                                            values=[ast.Name(id='e', ctx=ast.Load())]
                                        )
                                    )
                                ]
                            )
                        )
                    ]
                )
            ],
            orelse=[],
            finalbody=[]
        )
        
        # Replace function body with try-except block
        self.changes.append((node, try_except))

def add_imports(tree):
    """Add necessary imports to the tree."""
    # Check if logging is already imported
    has_logging_import = False
    for node in tree.body:
        if isinstance(node, ast.Import):
            for name in node.names:
                if name.name == 'logging':
                    has_logging_import = True
                    break
        elif isinstance(node, ast.ImportFrom):
            if node.module == 'logging':
                has_logging_import = True
                break
    
    # Add logging import if needed
    if not has_logging_import:
        tree.body.insert(0, ast.Import(names=[ast.alias(name='logging', asname=None)]))

def implement_error_handling():
    """Implement proper error handling in view functions."""
    for app_name in APPS:
        print(f"Implementing error handling for {app_name} app...")
        app_dir = PROJECT_ROOT / app_name
        
        # Skip if app directory doesn't exist
        if not app_dir.exists():
            print(f"  Skipping non-existent app: {app_name}")
            continue
        
        # Process views.py file
        views_path = app_dir / 'views.py'
        if not views_path.exists():
            print(f"  Skipping non-existent views.py file for {app_name}")
            continue
        
        # Read views.py file
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"  Skipping views.py file with syntax error for {app_name}")
            continue
        
        # Add error handling
        visitor = ErrorHandlingVisitor()
        visitor.visit(tree)
        
        # Apply changes
        if visitor.changes:
            print(f"  Adding error handling to {len(visitor.changes)} functions in {app_name}/views.py")
            
            # Add necessary imports
            add_imports(tree)
            
            # Apply changes to function bodies
            for node, try_except in visitor.changes:
                node.body = [try_except]
            
            # Generate code from modified tree
            new_content = ast.unparse(tree)
            
            # Write new content to file
            with open(views_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

if __name__ == "__main__":
    print("Implementing error handling...")
    implement_error_handling()
    print("Done!")
