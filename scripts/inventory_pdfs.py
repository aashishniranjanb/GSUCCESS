import os, hashlib, json

docs_dir = r"C:\Users\Home\Downloads\PROJECTS\SRE_APP\BASELINE docs"
pdfs = []
for f in sorted(os.listdir(docs_dir)):
    fp = os.path.join(docs_dir, f)
    if not os.path.isfile(fp):
        continue
    size = os.path.getsize(fp)
    sha = hashlib.sha256(open(fp, 'rb').read()).hexdigest()
    pdfs.append({"filename": f, "size_bytes": size, "sha256": sha})
    print(f"{f:80s} {size:>10,} bytes  sha256={sha[:16]}...")

print(f"\nTotal files: {len(pdfs)}")
with open("baseline_pdf_inventory.json", "w") as out:
    json.dump(pdfs, out, indent=2)
print("Written baseline_pdf_inventory.json")
