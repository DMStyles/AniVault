with open(r'C:\Users\dilsh\.gemini\antigravity\brain\29297739-d936-447d-9a40-3028faa6b52c\.system_generated\steps\309\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'ajax\/episode\/list\/', text)
for m in matches:
    start = max(0, m.start() - 100)
    end = min(len(text), m.end() + 200)
    print(text[start:end])
    print("-" * 60)
