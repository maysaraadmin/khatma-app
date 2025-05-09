#!/usr/bin/env python
"""
Script to optimize database queries.
This script analyzes view functions and adds select_related() and prefetch_related() where appropriate.
"""

import os
import re
import ast
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

class QueryOptimizer(ast.NodeVisitor):
    """AST visitor to optimize database queries."""
    
    def __init__(self):
        self.changes = []
        self.foreign_key_fields = {}
        self.many_to_many_fields = {}
    
    def visit_Assign(self, node):
        """Visit assignment node."""
        # Check if assignment involves a queryset
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                # Check if it's a queryset method
                if node.value.func.attr in ['all', 'filter', 'exclude', 'get']:
                    # Check if we need to add select_related or prefetch_related
                    self.optimize_queryset(node)
        
        self.generic_visit(node)
    
    def optimize_queryset(self, node):
        """Optimize a queryset by adding select_related() or prefetch_related()."""
        # Check if queryset already has select_related or prefetch_related
        if self.has_optimization(node.value):
            return
        
        # Get the model being queried
        model_name = self.get_model_name(node.value)
        if not model_name:
            return
        
        # Get foreign key fields for the model
        fk_fields = self.foreign_key_fields.get(model_name, [])
        m2m_fields = self.many_to_many_fields.get(model_name, [])
        
        # Check if we need to add select_related
        if fk_fields:
            # Create select_related call
            select_related_call = ast.Call(
                func=ast.Attribute(
                    value=node.value,
                    attr='select_related',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            )
            
            # Add field arguments
            for field in fk_fields:
                select_related_call.args.append(ast.Str(s=field))
            
            # Replace original call with optimized call
            self.changes.append((node, select_related_call))
        
        # Check if we need to add prefetch_related
        if m2m_fields:
            # Create prefetch_related call
            prefetch_related_call = ast.Call(
                func=ast.Attribute(
                    value=node.value if not fk_fields else select_related_call,
                    attr='prefetch_related',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[]
            )
            
            # Add field arguments
            for field in m2m_fields:
                prefetch_related_call.args.append(ast.Str(s=field))
            
            # Replace original call with optimized call
            if fk_fields:
                self.changes.append((node, prefetch_related_call))
            else:
                self.changes.append((node, prefetch_related_call))
    
    def has_optimization(self, node):
        """Check if a queryset already has select_related or prefetch_related."""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['select_related', 'prefetch_related']:
                    return True
                return self.has_optimization(node.func.value)
        return False
    
    def get_model_name(self, node):
        """Get the model name from a queryset call."""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    return node.func.value.id
                elif isinstance(node.func.value, ast.Attribute):
                    if node.func.value.attr == 'objects':
                        if isinstance(node.func.value.value, ast.Name):
                            return node.func.value.value.id
        return None

def load_model_relationships():
    """Load foreign key and many-to-many relationships from models."""
    relationships = {}
    
    for app_name in APPS:
        app_dir = PROJECT_ROOT / app_name
        
        # Skip if app directory doesn't exist
        if not app_dir.exists():
            continue
        
        # Process models.py file
        models_path = app_dir / 'models.py'
        if not models_path.exists():
            continue
        
        # Read models.py file
        with open(models_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue
        
        # Find model classes and their relationships
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                model_name = node.name
                fk_fields = []
                m2m_fields = []
                
                # Find field definitions
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                field_name = target.id
                                
                                # Check if it's a foreign key
                                if isinstance(item.value, ast.Call):
                                    if isinstance(item.value.func, ast.Name):
                                        if item.value.func.id in ['ForeignKey', 'OneToOneField']:
                                            fk_fields.append(field_name)
                                        elif item.value.func.id == 'ManyToManyField':
                                            m2m_fields.append(field_name)
                
                # Store relationships
                relationships[model_name] = {
                    'foreign_keys': fk_fields,
                    'many_to_many': m2m_fields
                }
    
    return relationships

def optimize_database_queries():
    """Optimize database queries in view functions."""
    # Load model relationships
    relationships = load_model_relationships()
    
    for app_name in APPS:
        print(f"Optimizing database queries for {app_name} app...")
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
        
        # Optimize queries
        optimizer = QueryOptimizer()
        optimizer.foreign_key_fields = {model: data['foreign_keys'] for model, data in relationships.items()}
        optimizer.many_to_many_fields = {model: data['many_to_many'] for model, data in relationships.items()}
        optimizer.visit(tree)
        
        # Apply changes
        if optimizer.changes:
            print(f"  Optimizing {len(optimizer.changes)} queries in {app_name}/views.py")
            
            # Sort changes in reverse order to avoid affecting earlier positions
            optimizer.changes.sort(key=lambda x: id(x[0]), reverse=True)
            
            for node, new_value in optimizer.changes:
                node.value = new_value
            
            # Generate code from modified tree
            new_content = ast.unparse(tree)
            
            # Write new content to file
            with open(views_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

if __name__ == "__main__":
    print("Optimizing database queries...")
    optimize_database_queries()
    print("Done!")
