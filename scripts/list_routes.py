import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r'@app\.(get|post|put|delete)\(\s*["\']([^"\']+)["\']')
matches = pattern.findall(text)

print(f"Total API routes in backend/main.py: {len(matches)}")
for method, route in matches:
    print(f"  {method.upper():6s} {route}")
