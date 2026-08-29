#!/usr/bin/env python
"""
Script to separate business logic from views.
This script analyzes view functions and extracts complex logic to service functions.
"""

import os
import re
import ast
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

class ViewAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze view functions."""
    
    def __init__(self):
        self.view_functions = []
        self.complex_views = []
        self.current_function = None
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        # Save current function
        old_function = self.current_function
        self.current_function = node
        
        # Check if this is a view function
        is_view = False
        if node.decorator_list:
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == 'login_required':
                    is_view = True
                elif isinstance(decorator, ast.Attribute) and decorator.attr == 'csrf_exempt':
                    is_view = True
        
        # Check function parameters
        if node.args.args and len(node.args.args) > 0:
            first_arg = node.args.args[0]
            if first_arg.arg == 'request':
                is_view = True
        
        if is_view:
            self.view_functions.append(node)
            
            # Check complexity
            complexity = self.calculate_complexity(node)
            if complexity > 10:  # Threshold for complex functions
                self.complex_views.append((node, complexity))
        
        # Visit children
        self.generic_visit(node)
        
        # Restore current function
        self.current_function = old_function
    
    def calculate_complexity(self, node):
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Start with 1
        
        # Count branches
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp) and isinstance(child.op, ast.And):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.BoolOp) and isinstance(child.op, ast.Or):
                complexity += len(child.values) - 1
        
        return complexity

def extract_business_logic(view_node):
    """Extract business logic from a view function."""
    # Create service function name
    service_name = f"{view_node.name}_service"
    
    # Create service function parameters
    params = []
    for arg in view_node.args.args:
        if arg.arg != 'request':
            params.append(arg)
    
    # Create service function body
    body = []
    for stmt in view_node.body:
        # Skip statements that directly use request
        if not uses_request(stmt):
            body.append(stmt)
    
    # Create service function
    service_func = ast.FunctionDef(
        name=service_name,
        args=ast.arguments(
            posonlyargs=[],
            args=params,
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            vararg=None,
            kwarg=None
        ),
        body=body,
        decorator_list=[],
        returns=None
    )
    
    # Add docstring
    docstring = f'"""Business logic for {view_node.name} view."""\n'
    service_func.body.insert(0, ast.Expr(ast.Str(s=docstring)))
    
    return service_func

def uses_request(node):
    """Check if a node uses the request object."""
    class RequestChecker(ast.NodeVisitor):
        def __init__(self):
            self.uses_request = False
        
        def visit_Name(self, node):
            if node.id == 'request':
                self.uses_request = True
            self.generic_visit(node)
    
    checker = RequestChecker()
    checker.visit(node)
    return checker.uses_request

def separate_business_logic():
    """Separate business logic from views."""
    for app_name in APPS:
        print(f"Analyzing views for {app_name} app...")
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
        
        # Analyze views
        analyzer = ViewAnalyzer()
        analyzer.visit(tree)
        
        print(f"  Found {len(analyzer.view_functions)} view functions")
        print(f"  Found {len(analyzer.complex_views)} complex view functions")
        
        # Create services.py file if complex views found
        if analyzer.complex_views:
            services_path = app_dir / 'services.py'
            
            # Check if services.py already exists
            if services_path.exists():
                print(f"  services.py already exists for {app_name}")
                with open(services_path, 'r', encoding='utf-8') as f:
                    services_content = f.read()
                services_tree = ast.parse(services_content)
            else:
                print(f"  Creating services.py for {app_name}")
                services_tree = ast.Module(
                    body=[
                        ast.Expr(ast.Str(s=f'"""Business logic for {app_name} app."""\n')),
                    ],
                    type_ignores=[]
                )
            
            # Extract business logic from complex views
            for view_node, complexity in analyzer.complex_views:
                print(f"  Extracting business logic from {view_node.name} (complexity: {complexity})")
                service_func = extract_business_logic(view_node)
                services_tree.body.append(service_func)
            
            # Write services.py file
            with open(services_path, 'w', encoding='utf-8') as f:
                f.write(ast.unparse(services_tree))

if __name__ == "__main__":
    print("Separating business logic from views...")
    separate_business_logic()
    print("Done!")
