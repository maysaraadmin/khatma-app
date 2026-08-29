import re
import os

files_to_clean = [
    r'D:\khatma-app\khatma\views.py',
    r'D:\khatma-app\core\views.py',
    r'D:\khatma-app\groups\views.py',
    r'D:\khatma-app\users\views.py',
    r'D:\khatma-app\chat\views.py',
    r'D:\khatma-app\notifications\views.py',
    r'D:\khatma-app\quran\views.py',
    r'D:\khatma-app\khatma\models.py',
    r'D:\khatma-app\users\models.py',
]

for filepath in files_to_clean:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remove standalone '\n' strings at module level (between imports)
    content = re.sub(r"^[ \t]*'\\n'[ \t]*\n", '', content, flags=re.MULTILINE)
    
    # Remove 'This module contains Module functionality.' strings
    content = re.sub(r"^[ \t]*'\"\"\"This module contains Module functionality.\"\"\"'[ \t]*\n", '', content, flags=re.MULTILINE)
    
    # Remove 'View for ...' strings inside functions (after try:)
    content = re.sub(r"([ \t]+try:\n[ \t]+)'View for [^']*'(\n)", r"\1\2", content, flags=re.MULTILINE)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Cleaned: {filepath}')
    else:
        print(f'No changes: {filepath}')
