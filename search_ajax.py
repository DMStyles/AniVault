with open(r'C:\Users\dilsh\.gemini\antigravity\brain\29297739-d936-447d-9a40-3028faa6b52c\.system_generated\steps\309\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Searching for Ajax endpoints inside main.js:")
matches = re.findall(r'ajax\/[a-zA-Z0-9_\-\/]+', text)
for m in set(matches):
    print(m)
