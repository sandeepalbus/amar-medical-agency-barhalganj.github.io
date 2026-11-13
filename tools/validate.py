# -*- coding: utf-8 -*-
"""Post-build checks: python3 tools/validate.py"""
import glob, json, os, re, sys, html
from collections import Counter
D = os.path.join(os.path.dirname(__file__), "..", "docs")
files = [f for f in glob.glob(D + "/**/index.html", recursive=True)] + [D + "/404.html"]
errs, titles, h1s, descs = [], Counter(), Counter(), Counter()
rows = []
def exists(link):
    link = link.split("#")[0].split("?")[0]
    if not link or link.startswith(("http", "mailto:", "tel:", "data:")): return True
    p = os.path.join(D, link.lstrip("/"))
    return os.path.isfile(p) or os.path.isfile(os.path.join(p, "index.html"))
for f in sorted(files):
    s = open(f, encoding="utf8").read(); rel = os.path.relpath(f, D)
    t = re.search(r"<title>(.*?)</title>", s, re.S).group(1); t = html.unescape(t)
    d = html.unescape(re.search(r'<meta name="description" content="(.*?)">', s, re.S).group(1))
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    titles[t] += 1; descs[d] += 1
    if len(h1) != 1: errs.append(f"{rel}: {len(h1)} h1")
    h1s[re.sub(r"<[^>]+>", "", h1[0]) if h1 else ""] += 1
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            j = json.loads(blk.replace("<\\/", "</"))
            for n in j["@graph"]:
                if "@type" not in n: errs.append(f"{rel}: node without @type")
        except Exception as e:
            errs.append(f"{rel}: bad JSON-LD {e}")
    ids = re.findall(r'\sid="([^"]+)"', s)
    for i, n in Counter(ids).items():
        if n > 1: errs.append(f"{rel}: duplicate id {i}")
    for l in re.findall(r'href="#([^"]+)"', s):
        if l not in ids: errs.append(f"{rel}: anchor #{l} has no target")
    for l in re.findall(r'(?:href|src)="([^"]+)"', s):
        if not exists(l): errs.append(f"{rel}: broken link {l}")
    for l in re.findall(r'srcset="([^"]+)"', s):
        if not exists(l.split()[0]): errs.append(f"{rel}: broken srcset {l}")
    if "<img" in s and re.search(r"<img(?![^>]*\balt=)", s): errs.append(f"{rel}: img without alt")
    if not re.search(r'<link rel="canonical" href="https://amarmedicalagency\.in', s): errs.append(f"{rel}: bad canonical")
    rows.append((rel, len(t), len(d), len(s.encode())))
for k, v in titles.items():
    if v > 1: errs.append(f"duplicate title x{v}: {k}")
for k, v in descs.items():
    if v > 1: errs.append(f"duplicate description x{v}: {k[:60]}")
for k, v in h1s.items():
    if v > 1: errs.append(f"duplicate h1 x{v}: {k}")
# sitemap vs pages
sm = re.findall(r"<loc>(.*?)</loc>", open(D + "/sitemap.xml").read())
pages = {"https://amarmedicalagency.in/" + os.path.relpath(f, D).replace("index.html", "") for f in files if not f.endswith("404.html")}
pages = {p.replace("//", "//") for p in pages}
if set(sm) != pages: errs.append(f"sitemap mismatch: missing={sorted(pages-set(sm))[:3]} extra={sorted(set(sm)-pages)[:3]}")
if any("vercel.app" in u for u in sm): errs.append("sitemap has vercel.app")
print("pages:", len(files), " sitemap urls:", len(sm))
print("title len max/avg:", max(r[1] for r in rows), sum(r[1] for r in rows)//len(rows), " desc len max/avg:", max(r[2] for r in rows), sum(r[2] for r in rows)//len(rows))
print("longest titles:", sorted(rows, key=lambda r: -r[1])[:4])
print("largest html:", max(r[3] for r in rows)//1024, "KB")
print("ERRORS:" if errs else "OK, no errors")
for e in errs: print(" -", e)
sys.exit(1 if errs else 0)
