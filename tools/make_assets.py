# -*- coding: utf-8 -*-
"""One-off: derive favicons + social share image from the owner's logo and storefront photo.
Run:  python3 tools/make_assets.py <dir with original images>
"""
import sys, os
import numpy as np
from PIL import Image

src = sys.argv[1]
out = os.path.join(os.path.dirname(__file__), "..", "docs", "assets", "img")

# --- favicon / app icons from the emblem (left part of the logo)
logo = Image.open(os.path.join(src, "amar-medical-logo.png")).convert("RGBA")
white = Image.new("RGBA", logo.size, (255, 255, 255, 255))
white.alpha_composite(logo)
gray = np.array(white.convert("L")) < 235
cols = np.where(gray[:, :500].any(axis=0))[0]
rows = np.where(gray[:, :500].any(axis=1))[0]
x0, x1, y0, y1 = cols.min(), cols.max(), rows.min(), rows.max()
emb = white.crop((x0, y0, x1 + 1, y1 + 1)).convert("RGB")
side = int(max(emb.size) * 1.22)
sq = Image.new("RGB", (side, side), (255, 255, 255))
sq.paste(emb, ((side - emb.width) // 2, (side - emb.height) // 2))
for name, px in [("icon-512.png", 512), ("icon-192.png", 192), ("apple-touch-icon.png", 180), ("favicon-48.png", 48)]:
    sq.resize((px, px), Image.LANCZOS).save(os.path.join(out, name), optimize=True)

# --- 1200x630 social share image (WhatsApp/Facebook previews prefer JPEG/PNG)
sf = Image.open(os.path.join(src, "home-storefront-desktop.jpg")).convert("RGB")
w, h = sf.size
th = round(w / (1200 / 630))
top = max(0, (h - th) // 2)
sf.crop((0, top, w, top + th)).resize((1200, 630), Image.LANCZOS).save(
    os.path.join(out, "og-default.jpg"), quality=80, optimize=True, progressive=True)
for n in ("icon-512.png", "icon-192.png", "apple-touch-icon.png", "favicon-48.png", "og-default.jpg"):
    print(n, os.path.getsize(os.path.join(out, n)) // 1024, "KB")
