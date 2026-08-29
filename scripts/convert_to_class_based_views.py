#!/usr/bin/env python
"""
Script to convert function-based views to class-based views.
This script analyzes view functions and converts them to class-based views where appropriate.
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
        self.current_function = None
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        # Save current function
        old_function = self.current_function
        self.current_function = node
        
        # Check if this is a view function
        is_view = False
        login_required = False
        
        if node.decorator_list:
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == 'login_required':
                    is_view = True
                    login_required = True
                elif isinstance(decorator, ast.Attribute) and decorator.attr == 'csrf_exempt':
                    is_view = True
        
        # Check function parameters
        if node.args.args and len(node.args.args) > 0:
            first_arg = node.args.args[0]
            if first_arg.arg == 'request':
                is_view = True
        
        if is_view:
            self.view_functions.append((node, login_required))
        
        # Visit children
        self.generic_visit(node)
        
        # Restore current function
        self.current_function = old_function

def determine_view_type(node):
    """Determine the type of class-based view to use."""
    # Check if view returns a list of objects
    returns_list = False
    returns_detail = False
    creates_object = False
    updates_object = False
    deletes_object = False
    
    # Check for common patterns in the function body
    for stmt in node.body:
        # Check for list view patterns
        if isinstance(stmt, ast.Assign):
            if isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Attribute):
                    if stmt.value.func.attr in ['all', 'filter']:
                        returns_list = True
        
        # Check for detail view patterns
        if isinstance(stmt, ast.Assign):
            if isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'get_object_or_404':
                    returns_detail = True
        
        # Check for create view patterns
        if isinstance(stmt, ast.If):
            if isinstance(stmt.test, ast.Compare):
                if isinstance(stmt.test.left, ast.Attribute) and stmt.test.left.attr == 'method':
                    if isinstance(stmt.test.comparators[0], ast.Str) and stmt.test.comparators[0].s == 'POST':
                        for substmt in stmt.body:
                            if isinstance(substmt, ast.If):
                                if isinstance(substmt.test, ast.Call):
                                    if isinstance(substmt.test.func, ast.Attribute) and substmt.test.func.attr == 'is_valid':
                                        creates_object = True
        
        # Check for update view patterns
        if isinstance(stmt, ast.If):
            if isinstance(stmt.test, ast.Compare):
                if isinstance(stmt.test.left, ast.Attribute) and stmt.test.left.attr == 'method':
                    if isinstance(stmt.test.comparators[0], ast.Str) and stmt.test.comparators[0].s == 'POST':
                        for substmt in stmt.body:
                            if isinstance(substmt, ast.If):
                                if isinstance(substmt.test, ast.Call):
                                    if isinstance(substmt.test.func, ast.Attribute) and substmt.test.func.attr == 'is_valid':
                                        if returns_detail:
                                            updates_object = True
        
        # Check for delete view patterns
        if isinstance(stmt, ast.If):
            if isinstance(stmt.test, ast.Compare):
                if isinstance(stmt.test.left, ast.Attribute) and stmt.test.left.attr == 'method':
                    if isinstance(stmt.test.comparators[0], ast.Str) and stmt.test.comparators[0].s == 'POST':
                        for substmt in stmt.body:
                            if isinstance(substmt, ast.Expr):
                                if isinstance(substmt.value, ast.Call):
                                    if isinstance(substmt.value.func, ast.Attribute) and substmt.value.func.attr == 'delete':
                                        deletes_object = True
    
    # Determine view type based on patterns
    if deletes_object:
        return 'DeleteView'
    elif updates_object:
        return 'UpdateView'
    elif creates_object:
        return 'CreateView'
    elif returns_detail:
        return 'DetailView'
    elif returns_list:
        return 'ListView'
    else:
        return 'View'

def convert_to_class_based_view(node, login_required):
    """Convert a function-based view to a class-based view."""
    view_type = determine_view_type(node)
    
    # Create class name from function name
    class_name = ''.join(word.capitalize() for word in node.name.split('_')) + view_type
    
    # Create class body
    body = []
    
    # Add model attribute if needed
    if view_type in ['ListView', 'DetailView', 'CreateView', 'UpdateView', 'DeleteView']:
        # Try to determine model from function body
        model_name = None
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                if isinstance(stmt.value, ast.Call):
                    if isinstance(stmt.value.func, ast.Attribute):
                        if hasattr(stmt.value.func, 'value') and hasattr(stmt.value.func.value, 'id'):
                            model_name = stmt.value.func.value.id
                            break
        
        if model_name:
            body.append(ast.Assign(
                targets=[ast.Name(id='model', ctx=ast.Store())],
                value=ast.Name(id=model_name, ctx=ast.Load())
            ))
    
    # Add template_name attribute
    template_name = None
    for stmt in node.body:
        if isinstance(stmt, ast.Return):
            if isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'render':
                    if len(stmt.value.args) >= 2 and isinstance(stmt.value.args[1], ast.Str):
                        template_name = stmt.value.args[1].s
                        break
    
    if template_name:
        body.append(ast.Assign(
            targets=[ast.Name(id='template_name', ctx=ast.Store())],
            value=ast.Str(s=template_name)
        ))
    
    # Add get_context_data method if needed
    context_vars = []
    for stmt in node.body:
        if isinstance(stmt, ast.Assign):
            if isinstance(stmt.targets[0], ast.Name) and stmt.targets[0].id == 'context':
                if isinstance(stmt.value, ast.Dict):
                    for i, key in enumerate(stmt.value.keys):
                        if isinstance(key, ast.Str):
                            context_vars.append(key.s)
    
    if context_vars:
        context_method = ast.FunctionDef(
            name='get_context_data',
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg='self', annotation=None)],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
                vararg=None,
                kwarg=ast.arg(arg='kwargs', annotation=None)
            ),
            body=[
                ast.Expr(ast.Str(s='"""Get additional context data."""')),
                ast.Assign(
                    targets=[ast.Name(id='context', ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Call(
                                func=ast.Name(id='super', ctx=ast.Load()),
                                args=[],
                                keywords=[]
                            ),
                            attr='get_context_data',
                            ctx=ast.Load()
                        ),
                        args=[],
                        keywords=[ast.keyword(arg='**kwargs', value=ast.Name(id='kwargs', ctx=ast.Load()))]
                    )
                ),
                ast.Return(value=ast.Name(id='context', ctx=ast.Load()))
            ],
            decorator_list=[],
            returns=None
        )
        body.append(context_method)
    
    # Create class definition
    bases = []
    if login_required:
        bases.append(ast.Name(id='LoginRequiredMixin', ctx=ast.Load()))
    bases.append(ast.Name(id=view_type, ctx=ast.Load()))
    
    class_def = ast.ClassDef(
        name=class_name,
        bases=bases,
        keywords=[],
        body=body,
        decorator_list=[]
    )
    
    # Add docstring
    docstring = f'"""Class-based view for {node.name}."""'
    class_def.body.insert(0, ast.Expr(ast.Str(s=docstring)))
    
    return class_def

def convert_to_class_based_views():
    """Convert function-based views to class-based views."""
    for app_name in APPS:
        print(f"Converting views for {app_name} app...")
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
        
        # Convert views
        for view_node, login_required in analyzer.view_functions:
            print(f"  Converting {view_node.name} to class-based view")
            class_def = convert_to_class_based_view(view_node, login_required)
            
            # Add class definition to tree
            tree.body.append(class_def)
        
        # Write updated views.py file
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(ast.unparse(tree))

if __name__ == "__main__":
    print("Converting function-based views to class-based views...")
    convert_to_class_based_views()
    print("Done!")
