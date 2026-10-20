import re

html = open('frontend/public/index.html', encoding='utf-8').read()
# match ${API_BASE}/api/... or '/api/...'
endpoints = set()
for match in re.finditer(r'(?:API_BASE|\'|\")(/api/[a-zA-Z0-9_\-\/\{\}]+)', html):
    endpoints.add(match.group(1))

for match in re.finditer(r'`\$\{API_BASE\}(/api/[a-zA-Z0-9_\-\/\{\}\$]+)', html):
    cleaned = re.sub(r'\$\{[^}]+\}', '{id}', match.group(1))
    endpoints.add(cleaned)

print(f"Total frontend endpoints invoked: {len(endpoints)}")
for ep in sorted(endpoints):
    print(f"  {ep}")
