import os
import re

def replace_in_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

replacements = [
    ('anivault-watchlist', 'kamiwatch-watchlist'),
    ('anivault-history', 'kamiwatch-history'),
    ('anivault-settings', 'kamiwatch-settings'),
    ('AniVault', 'KamiWatch'),
]

for root, dirs, files in os.walk('src'):
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git']]
    for fname in files:
        if fname.endswith(('.jsx', '.js', '.ts', '.tsx', '.css')):
            fpath = os.path.join(root, fname)
            replace_in_file(fpath, replacements)
            print(f"Processed: {fpath}")

print("Done!")
