"""Build both CVs and check what an applicant tracking system will see.

    uv run --with pypdf --with pdfminer.six python check.py

Fails if a CV runs over its page limit, if two common PDF text readers disagree with the source on key words,
or if words come out run together (justified or tightly kerned text does this in some readers).
"""
import re
import subprocess
import sys

import pypdf
from pdfminer.high_level import extract_text

CVS = {"Sadeeq_Adeyemi_CV_Industry": 1, "Sadeeq_Adeyemi_CV_Research": 1}
MUST_READ = ["Sadeeq Adeyemi", "AWS Certified", "multi-object tracking", "Kalman", "University of Maine"]

ok = True
for name, pages in CVS.items():
    subprocess.run(["tectonic", "-c", "minimal", f"{name}.tex"], check=True, capture_output=True)
    reader = pypdf.PdfReader(f"{name}.pdf")
    texts = {"pypdf": "\n".join(p.extract_text() for p in reader.pages), "pdfminer": extract_text(f"{name}.pdf")}
    problems = []
    if len(reader.pages) > pages:
        problems.append(f"{len(reader.pages)} pages, limit {pages}")
    for tool, text in texts.items():
        flat = " ".join(text.split())
        problems += [f"{tool} cannot read '{w}'" for w in MUST_READ if w.lower() not in flat.lower()]
        problems += [f"{tool} runs words together: {w}" for w in re.findall(r"[a-z]{3,}[A-Z]?[a-z]{14,}", text)[:3]]
    print(f"{name}: {len(reader.pages)} page(s), " + ("OK" if not problems else "; ".join(problems)))
    ok &= not problems
sys.exit(0 if ok else 1)
