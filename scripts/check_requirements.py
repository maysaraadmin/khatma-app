import os
import re
from pathlib import Path

# Define the project root directory
PROJECT_ROOT = Path(__file__).parent

# Known standard library modules that don't need to be in requirements.txt
STDLIB_MODULES = {
    'os', 're', 'sys', 'json', 'datetime', 'time', 'math', 'random', 'typing',
    'collections', 'itertools', 'functools', 'operator', 'hashlib', 'base64',
    'urllib', 'uuid', 'pathlib', 'shutil', 'tempfile', 'io', 'csv', 'logging'
}

# Find all Python files in the project
def find_python_files():
    python_files = []
    for root, _, files in os.walk(PROJECT_ROOT):
        # Skip virtual environment and other directories
        if any(skip in root for skip in ['venv', '.venv', '__pycache__', '.git', 'migrations']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    return python_files

# Extract imports from a Python file
def extract_imports(file_path):
    imports = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Find import statements
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith(('import ', 'from ')) and '#' not in line.split('#')[0]:
                # Handle from ... import ...
                if line.startswith('from '):
                    module = line.split()[1]
                    # Only get the base package (first part before dot)
                    if '.' in module:
                        module = module.split('.')[0]
                    if module not in STDLIB_MODULES:
                        imports.add(module)
                # Handle import ...
                elif line.startswith('import '):
                    modules = [m.strip() for m in line[7:].split(',')]
                    for module in modules:
                        # Handle 'as' aliases
                        if ' as ' in module:
                            module = module.split(' as ')[0].strip()
                        # Only get the base package (first part before dot)
                        if '.' in module:
                            module = module.split('.')[0]
                        if module not in STDLIB_MODULES:
                            imports.add(module)
    return imports

# Get installed packages from requirements.txt
def get_installed_packages():
    requirements_file = PROJECT_ROOT / 'requirements.txt'
    installed = set()
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (remove version specifiers)
                    pkg = re.split(r'[<>=!~]', line)[0].strip()
                    # Handle case with package name in URL or other formats
                    if '://' in pkg or '/' in pkg:
                        continue
                    installed.add(pkg.lower())
    return installed

# Main function
def main():
    print("🔍 Scanning project for Python imports...")
    
    # Get all Python files
    python_files = find_python_files()
    print(f"Found {len(python_files)} Python files")
    
    # Get all imports
    all_imports = set()
    for file_path in python_files:
        all_imports.update(extract_imports(file_path))
    
    # Filter out Django and Python standard library imports
    django_imports = {imp for imp in all_imports if imp.startswith('django')}
    other_imports = {
        imp for imp in all_imports 
        if not imp.startswith('django') and imp not in STDLIB_MODULES
    }
    
    # Get installed packages
    installed = get_installed_packages()
    
    # Find missing dependencies
    missing_deps = set()
    for imp in other_imports:
        # Map import names to package names
        pkg_name = imp.replace('_', '-').lower()
        if pkg_name not in installed and imp not in installed:
            missing_deps.add(imp)
    
    # Print results
    print("\n📦 Current requirements.txt packages:")
    for pkg in sorted(installed):
        print(f"  - {pkg}")
    
    print("\n🔍 Found the following Django imports:")
    for imp in sorted(django_imports):
        print(f"  - {imp}")
    
    if other_imports:
        print("\n🔍 Found the following non-Django imports:")
        for imp in sorted(other_imports):
            if imp in missing_deps:
                print(f"  - {imp} (MISSING from requirements.txt)")
            else:
                print(f"  - {imp}")
    
    if missing_deps:
        print("\n❌ Missing dependencies in requirements.txt:")
        for dep in sorted(missing_deps):
            print(f"  - {dep}")
    else:
        print("\n✅ All dependencies are properly listed in requirements.txt")

if __name__ == "__main__":
    main()
