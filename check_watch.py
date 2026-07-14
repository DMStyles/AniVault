import re

path = r'C:\Users\dilsh\.gemini\antigravity\brain\29297739-d936-447d-9a40-3028faa6b52c\.system_generated\steps\14\content.md'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

print('Searching for ajax/endpoints:')
urls = re.findall(r'\/ajax\/[a-zA-Z0-9_\-\/]+', text)
for u in set(urls):
    print(u)

print('\nSearching for script elements:')
scripts = re.findall(r'<script[^>]+>', text)
for s in scripts:
    if 'src' in s:
        print(s)
