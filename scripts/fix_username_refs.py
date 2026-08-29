import os

template_files = [
    r'D:\khatma-app\core\templates\core\community_leaderboard.html',
    r'D:\khatma-app\core\templates\core\base.html',
    r'D:\khatma-app\core\templates\core\my_profile.html',
    r'D:\khatma-app\core\templates\core\profile.html',
    r'D:\khatma-app\core\templates\core\user_profile.html',
]

for filepath in template_files:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = content.replace('{{ user.username }}', '{{ user.email }}')
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed: {filepath}')
    else:
        print(f'No changes: {filepath}')
