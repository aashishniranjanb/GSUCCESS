import csv

with open('reports/content_integrity_findings.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    issues = [r for r in reader if r['issues'] != 'NONE']

print(f"Total questions with findings: {len(issues)}")
for r in issues:
    print(f"{r['question_id']:22s} | {r['issues']:35s} | {r['stem_preview']}")
