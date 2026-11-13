# -*- coding: utf-8 -*-
"""Static site generator for amarmedicalagency.in  (python3 tools/build.py)

No dependencies. Output goes to docs/ (deploy that folder to GitHub Pages / Vercel / Cloudflare Pages).
All facts come from config.py; all medical text comes from content_*.py.
"""
import hashlib
import html
import json
import os
import re
import shutil
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from config import *  # noqa
import content_ortho, content_derm, content_ent  # noqa

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "docs")
E = lambda s: html.escape(str(s), quote=True)

# ------------------------------------------------------------------ data
SPEC = {
    "ortho": {"label": "हड्डी और जोड़", "full": "हड्डी, जोड़ और रीढ़", "icon": "bone", "mod": content_ortho,
              "blurb": "कमर, गर्दन, घुटने, कंधे और चोट"},
    "skin": {"label": "त्वचा और बाल", "full": "त्वचा और बाल", "icon": "drop", "mod": content_derm,
             "blurb": "दाद-खाज-खुजली, बाल, मुंहासे, एलर्जी"},
    "ent": {"label": "नाक, कान और गला", "full": "नाक, कान और गला (ENT)", "icon": "ear", "mod": content_ent,
            "blurb": "कान दर्द, गला, साइनस, सुनने की कमी"},
}
CONDS, BY_SLUG = [], {}
for k, m in SPEC.items():
    for c in m["mod"].CONDITIONS:
        c["spec"] = k
        c["url"] = f"/conditions/{c['slug']}/"
        c["chip"] = re.split(r"[(/]", c["hi"])[0].strip()
        c["en_short"] = c["en"].split("/")[0].strip()
        CONDS.append(c)
        BY_SLUG[c["slug"]] = c
assert len(BY_SLUG) == len(CONDS), "duplicate condition slug"

PAGES = []  # (url, priority-ish label) for sitemap


def wa(text=None):
    return f"https://wa.me/{WHATSAPP}" + (f"?text={quote(text)}" if text else "")


def doc_wa(d):
    return wa(f"नमस्ते, मुझे {d['name']} की OPD ({d['day_hi']}) के बारे में जानकारी चाहिए।")


def short_hi(s, n):
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


# ------------------------------------------------------------------ icons
ICONS = {
    "bone": '<path d="M17 10c.7-.7 1.69 0 2.5 0a2.5 2.5 0 1 0 0-5 .5.5 0 0 1-.5-.5 2.5 2.5 0 1 0-5 0c0 .81.7 1.8 0 2.5l-7 7c-.7.7-1.69 0-2.5 0a2.5 2.5 0 0 0 0 5c.28 0 .5.22.5.5a2.5 2.5 0 1 0 5 0c0-.81-.7-1.8 0-2.5Z"/>',
    "drop": '<path d="M12 2.7s6 6.4 6 10.3a6 6 0 0 1-12 0c0-3.9 6-10.3 6-10.3z"/>',
    "ear": '<path d="M6 8.5a6.5 6.5 0 1 1 13 0c0 6-6 6-6 10a3.5 3.5 0 1 1-7 0"/><path d="M15 8.5a2.5 2.5 0 0 0-5 0v1a2 2 0 1 1 0 4"/>',
    "wa": '<path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3z"/><path d="M9 8.5c0 3.5 3 6.5 6.5 6.5l1-1.5-2-1-1 .8c-1-.4-1.9-1.3-2.3-2.3l.8-1-1-2z"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/>',
    "pill": '<path d="M10.5 20.5 3.5 13.5a4.95 4.95 0 0 1 7-7l7 7a4.95 4.95 0 0 1-7 7z"/><path d="m8.5 8.5 7 7"/>',
    "check": '<path d="M5 12l5 5L20 7"/>',
    "go": '<path d="M9 6l6 6-6 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "alert": '<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v4M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
}
SPRITE = '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">' + "".join(
    f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items()) + "</svg>"


def ico(name):
    return f'<svg class="ico" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


# ------------------------------------------------------------------ schema.org
def jl(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"


def u(path):
    return DOMAIN + path


PH_ID, WEB_ID = u("/#pharmacy"), u("/#website")


def pharmacy_node():
    return {
        "@type": "Pharmacy", "@id": PH_ID, "name": NAME_HI, "alternateName": NAME_EN, "url": u("/"),
        "description": "बड़हलगंज (गोरखपुर) में दवा की दुकान, जहाँ हड्डी, त्वचा और ENT के विशेषज्ञ डॉक्टरों की साप्ताहिक OPD भी होती है। / Pharmacy with weekly orthopedic, dermatology and ENT OPD in Barhalganj, Gorakhpur.",
        "image": [u("/assets/img/og-default.jpg"), u("/assets/img/storefront-d.webp")],
        "logo": u("/assets/img/icon-512.png"),
        "telephone": "+" + EMERGENCY_PHONE,
        "address": {"@type": "PostalAddress", "streetAddress": STREET_HI, "addressLocality": CITY_HI,
                    "addressRegion": STATE_HI, "postalCode": PIN, "addressCountry": "IN"},
        "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
        "hasMap": MAPS_URL,
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": OPEN_TIME, "closes": CLOSE_TIME}],
        "areaServed": [{"@type": "Place", "name": a} for a in AREAS],
        "contactPoint": [{"@type": "ContactPoint", "contactType": "customer support", "telephone": "+" + WHATSAPP,
                          "availableLanguage": ["Hindi", "English"]}],
        "employee": {"@type": "Person", "name": "Raj Dubey", "jobTitle": "Pharmacist and Proprietor"},
        "sameAs": [FACEBOOK, INSTAGRAM, YOUTUBE, MAPS_URL],
    }


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items() if v is not None}
    if isinstance(o, list):
        return [clean(x) for x in o]
    return o


def website_node():
    return {"@type": "WebSite", "@id": WEB_ID, "url": u("/"), "name": NAME_HI, "alternateName": NAME_EN,
            "inLanguage": "hi-IN", "publisher": {"@id": PH_ID}}


def physician_node(d):
    spec_conditions = [c["en_short"] for c in CONDS if c["spec"] == d["key"]]
    hours = {"@type": "OpeningHoursSpecification", "dayOfWeek": d["day_schema"], "opens": d["opens"]}
    if d["closes"]:
        hours["closes"] = d["closes"]
    return {
        "@type": "Physician", "@id": u(f"/{d['slug']}/#physician"), "name": d["name_en"], "alternateName": d["name"],
        "description": f"{d['title_en']} holding OPD at Amar Medical Agency, College Tiraha, Barhalganj, Gorakhpur every {d['day_schema']}.",
        "medicalSpecialty": d["schema_specialty"], "url": u(f"/{d['slug']}/"),
        "image": u("/assets/img/" + d["photo"]),
        "address": pharmacy_node()["address"], "location": {"@id": PH_ID},
        "openingHoursSpecification": hours, "availableLanguage": ["Hindi", "English"],
        "knowsAbout": spec_conditions,
    }


def crumb_node(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": u(p)} if p else {})}
        for i, (n, p) in enumerate(trail)]}


def faq_node(faqs):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


# ------------------------------------------------------------------ shell
CSS_TXT = open(os.path.join(os.path.dirname(__file__), "assets", "site.css"), encoding="utf8").read()
CSS_TXT = re.sub(r"/\*.*?\*/", "", CSS_TXT, flags=re.S)
CSS_TXT = re.sub(r"\s+", " ", CSS_TXT)
CSS_TXT = re.sub(r"\s*([{};])\s*", r"\1", CSS_TXT).strip()
JS_TXT = open(os.path.join(os.path.dirname(__file__), "assets", "site.js"), encoding="utf8").read()
JS_TXT = re.sub(r"^\s*//.*$", "", JS_TXT, flags=re.M)
JS_TXT = re.sub(r"/\*.*?\*/", "", JS_TXT, flags=re.S)
JS_TXT = re.sub(r"\n\s*\n+", "\n", JS_TXT).strip()
CSS_V = hashlib.md5(CSS_TXT.encode()).hexdigest()[:8]
JS_V = hashlib.md5(JS_TXT.encode()).hexdigest()[:8]

NAV = [("होम", "/", "home"), ("डॉक्टर और OPD", "/doctors/", "doctors"), ("लक्षण और बीमारियाँ", "/conditions/", "cond"),
       ("दवाइयाँ", "/medicines/", "meds"), ("लोकेशन", "/location/", "loc"), ("हमारे बारे में", "/about/", "about")]


def layout(*, title, desc, path, body, graph, active="", wa_text=None, hero_preload="", og_image="/assets/img/og-default.jpg",
           noindex=False, lang="hi"):
    canon = u(path)
    nav_d = "".join(f'<a href="{p}"{" aria-current=page" if a == active else ""}>{E(n)}</a>' for n, p, a in NAV)
    nav_m = nav_d
    call_btn = ""
    if PROMOTE_CALL_BUTTON:
        call_btn = f'<a class="btn btn-ghost" href="tel:+{EMERGENCY_PHONE}" aria-label="फोन करें">{ico("phone")}</a>'
    bar = (f'<div class="bar" role="region" aria-label="त्वरित संपर्क">'
           f'<a class="btn btn-wa" href="{E(wa(wa_text or "नमस्ते, मुझे अमर मेडिकल एजेन्सी से जानकारी चाहिए।"))}" rel="noopener">{ico("wa")} WhatsApp पर पूछें</a>'
           f'{call_btn}<a class="btn btn-ghost" href="{MAPS_URL}" rel="noopener" target="_blank">{ico("pin")} रास्ता</a></div>')
    robots = "noindex,follow" if noindex else "index,follow,max-image-preview:large,max-snippet:-1"
    g = {"@context": "https://schema.org", "@graph": clean(graph)}
    og = u(og_image)
    head = f"""<!doctype html>
<html lang="{lang}" data-wa="{WHATSAPP}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#0b3fa8">
<meta property="og:type" content="website"><meta property="og:locale" content="hi_IN">
<meta property="og:site_name" content="{E(NAME_HI)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/favicon-48.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preload" href="/assets/fonts/hind-devanagari-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/hind-devanagari-700.woff2" as="font" type="font/woff2" crossorigin>
{hero_preload}<link rel="stylesheet" href="/assets/css/site.css?v={CSS_V}">
{jl(g)}
</head>"""
    header = f"""<body>
<a class="skip" href="#main">मुख्य सामग्री पर जाएँ</a>
{SPRITE}
<header class="site"><div class="container row">
<a class="logo" href="/" aria-label="{E(NAME_HI)}, होम"><img src="/assets/img/logo.webp" width="560" height="124" alt="{E(NAME_HI)} — {E(ADDRESS_SHORT_HI)}"></a>
<nav class="dnav" aria-label="मुख्य मेनू">{nav_d}</nav>
<details class="menu"><summary>{ico("menu")} मेनू</summary><nav aria-label="मोबाइल मेनू">{nav_m}</nav></details>
</div></header>
<main id="main">"""
    footer = f"""</main>
<footer><div class="container">
<div class="cols">
<div><h2>{E(NAME_HI)}</h2>
<p>{E(ADDRESS_HI)}</p>
<p>दुकान का समय: {E(HOURS_HI)}</p>
<p><a href="{MAPS_URL}" rel="noopener" target="_blank">Google Maps पर रास्ता देखें</a></p>
<div class="social"><a href="{FACEBOOK}" rel="noopener" aria-label="Facebook">f</a><a href="{INSTAGRAM}" rel="noopener" aria-label="Instagram">IG</a><a href="{YOUTUBE}" rel="noopener" aria-label="YouTube">▶</a></div></div>
<div><h2>डॉक्टर और OPD</h2><ul>
<li><a href="/{DOCTORS['ortho']['slug']}/">बड़हलगंज में हड्डी के डॉक्टर</a></li>
<li><a href="/{DOCTORS['skin']['slug']}/">बड़हलगंज में स्किन डॉक्टर</a></li>
<li><a href="/{DOCTORS['ent']['slug']}/">बड़हलगंज में ENT डॉक्टर</a></li>
<li><a href="/conditions/">लक्षण और बीमारियाँ</a></li></ul></div>
<div><h2>संपर्क</h2>
<p><a href="{wa()}" rel="noopener">WhatsApp: {WHATSAPP_DISPLAY}</a></p>
<p>आपातकालीन संपर्क: {EMERGENCY_PHONE_DISPLAY}</p>
<ul><li><a href="/about/">हमारे बारे में</a></li><li><a href="/medicines/">दवाइयाँ</a></li><li><a href="/location/">लोकेशन</a></li><li><a href="/privacy/">Privacy Policy</a></li><li><a href="/terms/">Terms &amp; Conditions</a></li></ul></div>
</div>
<p class="disc"><strong>सूचना:</strong> इस वेबसाइट की स्वास्थ्य जानकारी सामान्य जागरूकता के लिए है। यह डॉक्टर की जाँच, निदान या इलाज का विकल्प नहीं है। किसी भी दवा का उपयोग डॉक्टर या फार्मासिस्ट की सलाह से ही करें। आपातकाल में तुरंत नज़दीकी अस्पताल जाएँ या 112 / एम्बुलेंस 108 पर कॉल करें।<br>© 2026 {E(NAME_HI)}, {E(CITY_HI)}, {E(DISTRICT_HI)}</p>
</div></footer>
{bar}
<script src="/assets/js/site.js?v={JS_V}" defer></script>
</body></html>"""
    return head + header + body + footer


def write(path, content):
    fp = os.path.join(OUT, path.strip("/"), "index.html") if not path.endswith((".html", ".txt", ".xml", ".json", ".webmanifest")) else os.path.join(OUT, path.strip("/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf8") as f:
        f.write(content)


def crumbs(trail):
    items = []
    for i, (n, p) in enumerate(trail):
        last = i == len(trail) - 1
        items.append(f'<li{" aria-current=page" if last else ""}>' + (E(n) if last else f'<a href="{p}">{E(n)}</a>') + "</li>")
    return f'<nav class="crumbs container" aria-label="breadcrumb"><ol>{"".join(items)}</ol></nav>'


def ul(items, cls=""):
    return f'<ul class="{cls}">' + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>"


def faq_html(faqs):
    out = ['<div class="faq">']
    for q, a in faqs:
        out.append(f"<details><summary>{E(q)}</summary><div class=\"ans\"><p>{E(a)}</p></div></details>")
    out.append("</div>")
    return "".join(out)


def schedule_line(d):
    return f"प्रत्येक {d['day_hi']}, {d['time_hi']}"


def doctor_card(d, chips=True, link=True):
    conds = [c for c in CONDS if c["spec"] == d["key"]][:6]
    chips_html = ""
    if chips:
        chips_html = '<ul class="mini">' + "".join(f'<li><a href="{c["url"]}">{E(c["chip"])}</a></li>' for c in conds) + "</ul>"
    more = f'<a class="link-more" href="/{d["slug"]}/">पूरी जानकारी और सभी समस्याएँ {ico("go")}</a>' if link else ""
    w, h = d["photo_size"]
    return f"""<article class="card doc">
<div class="top"><div class="ph"><img src="/assets/img/{d['photo']}" width="{w}" height="{h}" loading="lazy" alt="{E(d['name'])} का चित्र"></div>
<div><span class="tag {d['color']}">{ico(SPEC[d['key']]['icon'])} {E(d['specialty_hi'])}</span>
<h3>{E(d['name'])}</h3><p class="role">{E(d['title'])}</p>
<p class="meta">{E(d['quals'])}<br>{E(d['inst'])}</p></div></div>
<div class="sched">{ico('cal')}<div>{E(schedule_line(d))}<small>समय अनुमानित है, आने से पहले WhatsApp पर पूछ लें</small></div></div>
{chips_html}
<a class="btn btn-wa btn-block" href="{E(doc_wa(d))}" rel="noopener">{ico('wa')} WhatsApp पर अपॉइंटमेंट पूछें</a>{more}
</article>"""


def opd_strip():
    out = ['<p class="today-line" data-today-line aria-live="polite"></p><div class="opd">']
    for k in ("ortho", "skin", "ent"):
        d = DOCTORS[k]
        out.append(f'<a class="day {k}" href="/{d["slug"]}/" data-day="{d["js_day"]}" data-name="{E(d["name"])}" data-time="{E(d["time_hi"])}">'
                   f'<div class="when" data-when>{E(d["day_hi"])}</div><div><b>{E(d["name"])}</b><span>{E(d["specialty_hi"])} · {E(d["time_hi"])}</span></div></a>')
    out.append("</div>")
    return "".join(out)


def picker(only=None):
    out = ['<div class="picker">']
    for k in ("ortho", "skin", "ent"):
        if only and k != only:
            continue
        d, m = DOCTORS[k], SPEC[k]
        chips = "".join(f'<a class="chip" href="{c["url"]}">{E(c["chip"])}</a>' for c in CONDS if c["spec"] == k)
        out.append(f'<div class="pgroup {k}"><h3><span class="badge">{ico(m["icon"])}</span>{E(m["label"])}</h3>'
                   f'<p>{E(d["name"])} · प्रत्येक {E(d["day_hi"])}</p><div class="chips">{chips}</div></div>')
    out.append("</div>")
    return "".join(out)


def cta_block(d=None, text="अपॉइंटमेंट और OPD की जानकारी के लिए WhatsApp पर लिखें"):
    link = doc_wa(d) if d else wa("नमस्ते, मुझे अमर मेडिकल एजेन्सी से जानकारी चाहिए।")
    who = f"{d['name']}: {schedule_line(d)}" if d else HOURS_HI
    return f"""<div class="cta"><div><h2>{E(text)}</h2><p>{E(who)} · {E(ADDRESS_SHORT_HI)}</p></div>
<div class="btns"><a class="btn btn-wa" href="{E(link)}" rel="noopener">{ico('wa')} WhatsApp पर पूछें</a>
<a class="btn btn-ghost" href="{MAPS_URL}" rel="noopener" target="_blank">{ico('pin')} रास्ता देखें</a></div></div>"""


# ------------------------------------------------------------------ pages
def page_home():
    trust = [
        "44 वर्षों से बड़हलगंज की सेवा में लगे 'अमर मेडिकल स्टोर' परिवार की नई शाखा",
        "AIIMS, BRD मेडिकल कॉलेज, SGPGI, KGMU, BHU जैसे अस्पतालों के पर्चे की दवाइयाँ",
        "दवा न होने पर तुरंत या 24 घंटे के भीतर मंगाने का प्रयास",
    ]
    trust_html = "".join(f"<li>{ico('check')}<span>{E(t)}</span></li>" for t in trust)
    cats = [("cat-baby", "बेबी केयर"), ("cat-diabetes", "डायबिटीज केयर"), ("cat-heart", "हार्ट, BP और कोलेस्ट्रॉल"),
            ("cat-vitamin", "विटामिन और सप्लिमेंट्स"), ("cat-personal", "पर्सनल केयर"), ("cat-general", "सामान्य दवाईयाँ")]
    cats_html = "".join(f'<div class="cat"><img src="/assets/img/{i}.webp" width="236" height="168" loading="lazy" alt=""><div>{E(n)}</div></div>' for i, n in cats)
    docs = "".join(doctor_card(DOCTORS[k]) for k in ("ortho", "skin", "ent"))
    landmarks = [("इंडियन ओवरसीज बैंक", "50 मीटर"), ("नेशनल इंटर कॉलेज", "250 मीटर"), ("बस स्टैंड (बाईपास)", "500 मीटर"), ("ब्लॉक कार्यालय (गोला रोड)", "1.5 किमी")]
    lm = "".join(f"<li><span>{E(a)}</span><span>{E(b)}</span></li>" for a, b in landmarks)
    areas = "".join(f"<span>{E(a)}</span>" for a in AREAS)
    body = f"""
<section class="hero"><div class="wrap">
<div class="pic"><picture><source media="(min-width:900px)" srcset="/assets/img/storefront-d.webp" width="1400" height="763">
<img src="/assets/img/storefront-m.webp" width="760" height="1013" alt="{E(NAME_HI)} की दुकान का सामने का दृश्य, कॉलेज तिराहा, बड़हलगंज" fetchpriority="high"></picture></div>
<div class="copy"><span class="eyebrow">{ico('pin')} कॉलेज तिराहा, बड़हलगंज, गोरखपुर</span>
<h1>बड़हलगंज में दवा और विशेषज्ञ डॉक्टर, एक ही जगह</h1>
<p class="lead">हड्डी, त्वचा और कान-नाक-गला (ENT) विशेषज्ञ डॉक्टरों की साप्ताहिक OPD और प्रमुख अस्पतालों की दवाइयाँ, आपके अपने कस्बे में।</p>
<p><span data-status class="status">{E(HOURS_HI)}</span></p>
<div class="btns"><a class="btn btn-wa btn-block" href="{E(wa('नमस्ते, मुझे OPD अपॉइंटमेंट की जानकारी चाहिए।'))}" rel="noopener">{ico('wa')} WhatsApp पर अपॉइंटमेंट पूछें</a>
<a class="btn btn-ghost btn-block" href="/doctors/">{ico('cal')} OPD का समय देखें</a></div>
<ul class="trust">{trust_html}</ul></div></div></section>

<section><div class="container"><div class="sec-head"><h2>इस हफ्ते की OPD</h2><a class="link-more" href="/doctors/">सभी डॉक्टर {ico('go')}</a></div>
{opd_strip()}</div></section>

<section style="background:#fff;border-block:1px solid var(--line)"><div class="container">
<div class="sec-head"><h2>आपको क्या परेशानी है?</h2><a class="link-more" href="/conditions/">सभी लक्षण {ico('go')}</a></div>
<p class="muted">अपनी समस्या चुनें। लक्षण, कारण, घर पर देखभाल और डॉक्टर को कब दिखाना है, सब हिंदी में।</p>
{picker()}</div></section>

<section><div class="container"><div class="sec-head"><h2>हमारे विशेषज्ञ डॉक्टर</h2></div>
<div class="grid c3">{docs}</div></div></section>

<section style="background:#fff;border-block:1px solid var(--line)"><div class="container">
<div class="sec-head"><h2>दवाइयाँ और हेल्थ प्रोडक्ट्स</h2><a class="link-more" href="/medicines/">पूरी जानकारी {ico('go')}</a></div>
<p>गोरखपुर, बड़हलगंज, लखनऊ और वाराणसी के प्रमुख अस्पतालों और विशेषज्ञ डॉक्टरों द्वारा लिखी दवाइयाँ हमारे यहाँ उपलब्ध रहती हैं। कोई दवा उपलब्ध न हो तो उसे तुरंत या 24 घंटे के भीतर मंगाने का हर संभव प्रयास करते हैं।</p>
<div class="cats">{cats_html}</div>
<p class="small muted" style="margin-top:14px">दवा उपलब्ध है या नहीं, WhatsApp पर दवा का नाम भेजकर पूछ सकते हैं। पर्चे वाली दवाइयाँ केवल डॉक्टर के पर्चे पर ही दी जाती हैं।</p></div></section>

<section><div class="container about">
<div class="ph"><img src="/assets/img/raj-dubey.webp" width="480" height="770" loading="lazy" alt="{E(PHARMACIST)}, संचालक एवं फार्मासिस्ट"></div>
<div><h2>सही दवा, सही सलाह</h2>
<p>बड़हलगंज (गोला रोड) में 44 वर्षों से अधिक समय से सेवा दे रहे 'अमर मेडिकल स्टोर' की सफलता और आपके भरोसे के बाद, 2026 में दूसरी शाखा 'अमर मेडिकल एजेन्सी' कॉलेज तिराहा पर शुरू हुई।</p>
<p><strong>{E(PHARMACIST)}</strong>, संचालक एवं फार्मासिस्ट। इससे पहले गोरखपुर AIIMS के समीप फार्मेसी का सफल संचालन।</p>
<a class="btn btn-ghost" href="/about/">हमारी कहानी पढ़ें {ico('go')}</a></div></div></section>

<section style="background:#fff;border-top:1px solid var(--line)"><div class="container where">
<div><h2>हमारा पता</h2><dl class="facts">
<div><dt>{ico('pin')} पता</dt><dd>{E(ADDRESS_HI)}</dd></div>
<div><dt>{ico('clock')} दुकान का समय</dt><dd>{E(HOURS_HI)}</dd></div></dl>
<div class="btns" style="margin-top:16px"><a class="btn btn-brand btn-block" href="{MAPS_URL}" rel="noopener" target="_blank">{ico('pin')} Google Maps पर खोलें</a></div></div>
<div><h3>पास के स्थान</h3><ul class="landmarks">{lm}</ul>
<h3 style="margin-top:18px">आसपास के क्षेत्र</h3><div class="areas">{areas}</div></div></div></section>
"""
    graph = [pharmacy_node(), website_node(), *[physician_node(DOCTORS[k]) for k in DOCTORS],
             {"@type": "WebPage", "@id": u("/#webpage"), "url": u("/"), "name": "अमर मेडिकल एजेन्सी, बड़हलगंज", "isPartOf": {"@id": WEB_ID},
              "about": {"@id": PH_ID}, "inLanguage": "hi-IN", "dateModified": BUILD_DATE}]
    pre = ('<link rel="preload" as="image" href="/assets/img/storefront-m.webp" media="(max-width:899px)" fetchpriority="high">\n'
           '<link rel="preload" as="image" href="/assets/img/storefront-d.webp" media="(min-width:900px)" fetchpriority="high">\n')
    write("/", layout(
        title="अमर मेडिकल एजेन्सी, बड़हलगंज | दवा और हड्डी, स्किन, ENT डॉक्टर",
        desc="कॉलेज तिराहा, बड़हलगंज (गोरखपुर) में दवा की दुकान और हड्डी, त्वचा व ENT विशेषज्ञ डॉक्टरों की साप्ताहिक OPD। समय, लक्षण की जानकारी और WhatsApp अपॉइंटमेंट।",
        path="/", body=body, graph=graph, active="home", hero_preload=pre))
    PAGES.append("/")


def page_doctors_hub():
    rows = "".join(
        f'<tr><td>{E(DOCTORS[k]["day_hi"])}</td><td><a href="/{DOCTORS[k]["slug"]}/">{E(DOCTORS[k]["name"])}</a></td><td>{E(DOCTORS[k]["title"])}</td><td>{E(DOCTORS[k]["time_hi"])}</td></tr>'
        for k in ("ortho", "skin", "ent"))
    opts = "".join(f'<option value="{k}">{E(DOCTORS[k]["name"])} ({E(DOCTORS[k]["specialty_hi"])}, {E(DOCTORS[k]["day_hi"])})</option>' for k in DOCTORS)
    faqs = [
        ("बड़हलगंज में कौन-कौन से विशेषज्ञ डॉक्टर बैठते हैं?",
         f"अमर मेडिकल एजेन्सी, कॉलेज तिराहा, बड़हलगंज में तीन विशेषज्ञों की साप्ताहिक OPD होती है: हड्डी रोग विशेषज्ञ {DOCTORS['ortho']['name']} (रविवार), त्वचा रोग विशेषज्ञ {DOCTORS['skin']['name']} (गुरुवार) और नाक-कान-गला विशेषज्ञ {DOCTORS['ent']['name']} (शुक्रवार)।"),
        ("OPD का समय क्या है?",
         f"{DOCTORS['ortho']['name']}: प्रत्येक रविवार {DOCTORS['ortho']['time_hi']}। {DOCTORS['skin']['name']}: प्रत्येक गुरुवार {DOCTORS['skin']['time_hi']}। {DOCTORS['ent']['name']}: प्रत्येक शुक्रवार {DOCTORS['ent']['time_hi']}। समय अनुमानित है, इसलिए आने से पहले WhatsApp पर पुष्टि कर लें।"),
        ("अपॉइंटमेंट कैसे लें?",
         f"WhatsApp {WHATSAPP_DISPLAY} पर संदेश भेजें या इस पेज का फ़ॉर्म भरें। फ़ॉर्म भरने या संदेश भेजने भर से अपॉइंटमेंट पक्का नहीं माना जाता। हमारी टीम के जवाब से पुष्टि लें।"),
        ("OPD में कितना इंतज़ार करना पड़ता है?",
         "OPD में लगभग डेढ़ से दो घंटे या उससे अधिक प्रतीक्षा हो सकती है। क्लिनिक पहुँचकर रिसेप्शन पर पंजीकरण कराएँ। देर से आने पर पहले से प्रतीक्षा कर रहे मरीजों को प्राथमिकता दी जाएगी।"),
        ("क्या पर्चे की दवाइयाँ यहीं मिल जाती हैं?",
         "गोरखपुर, लखनऊ और वाराणसी के प्रमुख अस्पतालों और विशेषज्ञ डॉक्टरों द्वारा लिखी दवाइयाँ हमारे यहाँ उपलब्ध रहती हैं। कोई दवा न हो तो उसे तुरंत या 24 घंटे के भीतर मंगाने का प्रयास किया जाता है।"),
        ("क्लिनिक कहाँ है?", f"{ADDRESS_HI}। Google Maps: {MAPS_URL}"),
    ]
    body = f"""{crumbs([("होम", "/"), ("डॉक्टर और OPD", None)])}
<div class="container phead"><h1>बड़हलगंज के विशेषज्ञ डॉक्टर और OPD समय सारणी</h1>
<p class="lead">हड्डी, त्वचा और कान-नाक-गला (ENT) के विशेषज्ञ, कॉलेज तिराहा, बड़हलगंज में हर हफ्ते। गोरखपुर तक न जाकर अपने कस्बे में परामर्श।</p>
<p class="small muted">{SPELLINGS}: जगह एक ही है, वर्तनी अलग-अलग लिखी जाती है।</p></div>
<section style="padding-top:8px"><div class="container">
<h2>साप्ताहिक OPD सारणी</h2>
<table class="tbl"><thead><tr><th>दिन</th><th>डॉक्टर</th><th>विशेषज्ञता</th><th>समय</th></tr></thead><tbody>{rows}</tbody></table>
<div class="box note"><h3>{ico('info')} OPD में आने से पहले</h3><ul>
<li>डॉक्टर का समय अनुमानित है। OPD में लगभग डेढ़ से दो घंटे या उससे अधिक प्रतीक्षा हो सकती है।</li>
<li>क्लिनिक पहुँचकर रिसेप्शन पर पंजीकरण कराएँ।</li>
<li>पुरानी रिपोर्ट, पर्चे और चल रही दवाइयाँ साथ लाएँ।</li></ul></div></div></section>
<section style="background:#fff;border-block:1px solid var(--line)"><div class="container"><h2>हमारे डॉक्टर</h2>
<div class="grid c3">{"".join(doctor_card(DOCTORS[k]) for k in ("ortho", "skin", "ent"))}</div></div></section>
<section id="book"><div class="container narrow"><h2>WhatsApp पर अपॉइंटमेंट पूछें</h2>
<p class="muted">नाम, मोबाइल और डॉक्टर चुनें। यह आपको WhatsApp पर हमारे पास ले जाएगा। यहाँ कुछ भी सेव नहीं होता। कृपया बीमारी की रिपोर्ट या पर्चे की फोटो इस फ़ॉर्म में न भेजें।</p>
<form class="form card" id="book-form" autocomplete="on">
<label>आपका नाम<input name="name" required autocomplete="name" placeholder="जैसे: रमेश यादव"></label>
<label>मोबाइल नंबर<input name="mobile" required inputmode="numeric" autocomplete="tel-national" placeholder="10 अंकों का नंबर" maxlength="14"></label>
<label>डॉक्टर चुनें<select name="doctor" required>{opts}</select></label>
<button class="btn btn-wa btn-block" type="submit">{ico('wa')} WhatsApp पर भेजें</button>
<noscript><p>फ़ॉर्म के लिए JavaScript चाहिए। सीधे <a href="{wa()}">WhatsApp पर संदेश भेजें</a>।</p></noscript></form></div></section>
<section style="background:#fff;border-top:1px solid var(--line)"><div class="container narrow"><h2>अक्सर पूछे जाने वाले प्रश्न</h2>{faq_html(faqs)}</div></section>
<div class="container">{cta_block()}</div>"""
    graph = [pharmacy_node(), website_node(), *[physician_node(DOCTORS[k]) for k in DOCTORS],
             {"@type": "CollectionPage", "@id": u("/doctors/#webpage"), "url": u("/doctors/"), "name": "बड़हलगंज के विशेषज्ञ डॉक्टर और OPD", "isPartOf": {"@id": WEB_ID}, "inLanguage": "hi-IN", "dateModified": BUILD_DATE},
             crumb_node([("होम", "/"), ("डॉक्टर और OPD", "/doctors/")]), faq_node(faqs)]
    write("/doctors/", layout(
        title="बड़हलगंज के विशेषज्ञ डॉक्टर और OPD समय | हड्डी, स्किन, ENT",
        desc="बड़हलगंज, गोरखपुर में हड्डी (रविवार), त्वचा (गुरुवार) और ENT (शुक्रवार) विशेषज्ञों की OPD का समय, योग्यता और WhatsApp अपॉइंटमेंट।",
        path="/doctors/", body=body, graph=graph, active="doctors"))
    PAGES.append("/doctors/")


SPEC_FAQ = {
    "ortho": lambda d: [
        ("बड़हलगंज में हड्डी के डॉक्टर कब बैठते हैं?",
         f"{d['name']} ({d['quals']}) प्रत्येक रविवार सुबह 10:30 बजे से अमर मेडिकल एजेन्सी, कॉलेज तिराहा, बड़हलगंज में OPD करते हैं। समय अनुमानित है, आने से पहले WhatsApp पर पुष्टि कर लें।"),
        ("बड़हलगंज में सबसे अच्छा हड्डी का डॉक्टर कौन है?",
         f"'सबसे अच्छा' कोई एक व्यक्ति तय नहीं कर सकता। डॉक्टर चुनते समय उनकी योग्यता, विशेषज्ञता, अनुभव और मरीजों के अनुभव देखें। यहाँ {d['name']} हड्डी रोग विशेषज्ञ हैं ({d['quals']}) और प्रत्येक रविवार OPD करते हैं।"),
        ("कमर दर्द, घुटने के दर्द और स्लिप डिस्क में कौन सा डॉक्टर दिखाएँ?",
         "ये हड्डी, जोड़ और रीढ़ की समस्याएँ हैं। इनके लिए ऑर्थोपेडिक विशेषज्ञ (हड्डी रोग विशेषज्ञ) को दिखाया जाता है।"),
        ("चोट लगने के बाद 'हड्डी बैठाने वाले' के पास जाना ठीक है?",
         "अगर फ्रैक्चर की आशंका हो तो पहले X-ray और डॉक्टर की जाँच ज़रूरी है। जोर-जबरदस्ती की खिंचाई से नस या खून की नली को नुकसान हो सकता है।"),
        ("क्या हड्डी की आम समस्याओं के लिए गोरखपुर जाना ज़रूरी है?",
         "कमर, गर्दन, घुटने, कंधे और चोट जैसी आम समस्याओं की जाँच और सलाह बड़हलगंज की OPD में उपलब्ध है। अगर डॉक्टर को आगे की जाँच या अस्पताल की सुविधा की ज़रूरत लगे तो वे उसकी सलाह देंगे।"),
    ],
    "skin": lambda d: [
        ("बड़हलगंज में स्किन डॉक्टर कब बैठते हैं?",
         f"{d['name']} ({d['quals']}) प्रत्येक गुरुवार दोपहर 2:00 बजे से 5:00 बजे तक अमर मेडिकल एजेन्सी, कॉलेज तिराहा, बड़हलगंज में OPD करती हैं। समय अनुमानित है, आने से पहले WhatsApp पर पुष्टि कर लें।"),
        ("बड़हलगंज में सबसे अच्छी स्किन डॉक्टर कौन हैं?",
         f"'सबसे अच्छा' कोई एक व्यक्ति तय नहीं कर सकता। डॉक्टर चुनते समय उनकी योग्यता, विशेषज्ञता, अनुभव और मरीजों के अनुभव देखें। यहाँ {d['name']} त्वचा रोग विशेषज्ञ हैं, {d['quals']}, और प्रत्येक गुरुवार OPD करती हैं।"),
        ("बाल झड़ने और गंजेपन में कौन सा डॉक्टर दिखाएँ?",
         "बाल, खोपड़ी और त्वचा की समस्याओं के लिए त्वचा रोग विशेषज्ञ (डर्मेटोलॉजिस्ट) को दिखाया जाता है। बालों के झड़ने के कई कारण होते हैं, इसलिए पहले कारण की जाँच ज़रूरी है।"),
        ("क्या दाद या खुजली की क्रीम खुद से लगा सकते हैं?",
         "बिना डॉक्टर की सलाह नहीं। कई क्रीमों में स्टेरॉयड मिला होता है, जो शुरू में आराम देता है पर संक्रमण को बढ़ाकर बार-बार लौटाने वाला बना सकता है। पहले पहचान कराएँ कि यह दाद है, खुजली (स्कैबीज़) है या कुछ और।"),
        ("क्या त्वचा की आम समस्याओं के लिए गोरखपुर जाना ज़रूरी है?",
         "दाद-खाज, बाल झड़ना, मुंहासे, रूसी, फंगल इंफेक्शन, नाखून और एलर्जी जैसी आम समस्याओं की जाँच और सलाह बड़हलगंज की OPD में उपलब्ध है। डॉक्टर को आगे की जाँच की ज़रूरत लगे तो वे उसकी सलाह देंगी।"),
    ],
    "ent": lambda d: [
        ("बड़हलगंज में ENT डॉक्टर कब बैठते हैं?",
         f"{d['name']} प्रत्येक शुक्रवार दोपहर 2:00 बजे से 5:00 बजे तक अमर मेडिकल एजेन्सी, कॉलेज तिराहा, बड़हलगंज में OPD करते हैं। समय अनुमानित है, आने से पहले WhatsApp पर पुष्टि कर लें।"),
        ("बड़हलगंज में सबसे अच्छा ENT डॉक्टर कौन है?",
         f"'सबसे अच्छा' कोई एक व्यक्ति तय नहीं कर सकता। डॉक्टर चुनते समय उनकी योग्यता, विशेषज्ञता, अनुभव और मरीजों के अनुभव देखें। यहाँ {d['name']} नाक-कान-गला रोग विशेषज्ञ हैं और प्रत्येक शुक्रवार OPD करते हैं।"),
        ("कान दर्द, कान बहना और सुनने की कमी में कौन सा डॉक्टर दिखाएँ?",
         "कान, नाक और गले की समस्याओं के लिए ENT (ई.एन.टी.) विशेषज्ञ को दिखाया जाता है।"),
        ("कान साफ़ करने के लिए तेल या तीली डाल सकते हैं?",
         "नहीं। कान में तेल, तीली, पिन या कॉटन बड्स न डालें। अगर पर्दे में छेद हो तो इनसे गंभीर नुकसान हो सकता है। कान की सफ़ाई डॉक्टर से कराएँ।"),
        ("क्या कान-नाक-गला की आम समस्याओं के लिए गोरखपुर जाना ज़रूरी है?",
         "कान दर्द, गले की खराश, टॉन्सिल, साइनस, आवाज़ बैठना और सुनने की कमी जैसी आम समस्याओं की जाँच और सलाह बड़हलगंज की OPD में उपलब्ध है। डॉक्टर को आगे की जाँच की ज़रूरत लगे तो वे उसकी सलाह देंगे।"),
    ],
}
SPEC_H1 = {
    "ortho": "बड़हलगंज में हड्डी के डॉक्टर (ऑर्थोपेडिक): {name}",
    "skin": "बड़हलगंज में स्किन डॉक्टर (त्वचा रोग विशेषज्ञ): {name}",
    "ent": "बड़हलगंज में ENT डॉक्टर (नाक, कान, गला): {name}",
}
SPEC_TITLE = {
    "ortho": "बड़हलगंज में हड्डी के डॉक्टर | {name} (MS Orthopedics)",
    "skin": "बड़हलगंज में स्किन डॉक्टर | {name} (MD Skin & VD)",
    "ent": "बड़हलगंज में ENT डॉक्टर (नाक-कान-गला) | {name}",
}
SPEC_LEAD = {
    "ortho": "कमर दर्द, स्लिप डिस्क, गर्दन (सर्वाइकल) दर्द, साइटिका, घुटने और कंधे का दर्द, हड्डियों की कमज़ोरी और खेल की चोट की जाँच और सलाह, गोरखपुर तक जाए बिना, बड़हलगंज में।",
    "skin": "दाद-खाज-खुजली, बालों का झड़ना, मुंहासे, फंगल इंफेक्शन, डैंड्रफ, नाखून की समस्या और स्किन एलर्जी की जाँच और सलाह, बड़हलगंज में।",
    "ent": "कान दर्द, कान बहना, गले का दर्द, टॉन्सिल, साइनस, आवाज़ बैठना, कान में आवाज़ और सुनने की कमी की जाँच और सलाह, बड़हलगंज में।",
}


def page_specialty(k):
    d, m = DOCTORS[k], SPEC[k]
    conds = [c for c in CONDS if c["spec"] == k]
    faqs = SPEC_FAQ[k](d)
    cards = "".join(
        f'<a class="card" style="display:block;text-decoration:none;color:inherit" href="{c["url"]}"><h3 style="margin-bottom:4px">{E(c["hi"])}</h3>'
        f'<p class="small muted" style="margin:0">{E(short_hi(c["intro"].split("।")[0] + "।", 110))}</p></a>' for c in conds)
    others = "".join(f'<a class="chip" href="/{DOCTORS[o]["slug"]}/">{E(SPEC[o]["label"])}: {E(DOCTORS[o]["name"])}</a>' for o in DOCTORS if o != k)
    areas = "".join(f"<span>{E(a)}</span>" for a in AREAS)
    w, h = d["photo_size"]
    body = f"""{crumbs([("होम", "/"), ("डॉक्टर और OPD", "/doctors/"), (m["label"], None)])}
<div class="container phead"><span class="tag {d['color']}">{ico(m['icon'])} {E(d['specialty_hi'])}</span>
<h1 style="margin-top:10px">{E(SPEC_H1[k].format(name=d['name']))}</h1>
<p class="lead">{E(SPEC_LEAD[k])}</p></div>
<section style="padding-top:8px"><div class="container grid c2" style="align-items:start">
<article class="card doc"><div class="top"><div class="ph" style="width:96px;height:120px"><img src="/assets/img/{d['photo']}" width="{w}" height="{h}" alt="{E(d['name'])} का चित्र" fetchpriority="high"></div>
<div><h2 style="margin:0 0 2px;font-size:1.3rem">{E(d['name'])}</h2><p class="role">{E(d['title'])}</p><p class="meta">{E(d['quals'])}<br>{E(d['inst'])}</p></div></div>
<div class="sched">{ico('cal')}<div>{E(schedule_line(d))}<small>समय अनुमानित है, आने से पहले WhatsApp पर पूछ लें</small></div></div>
<dl class="facts"><div><dt>{ico('pin')} स्थान</dt><dd>{E(NAME_HI)}, {E(ADDRESS_SHORT_HI)}</dd></div></dl>
<a class="btn btn-wa btn-block" href="{E(doc_wa(d))}" rel="noopener">{ico('wa')} WhatsApp पर अपॉइंटमेंट पूछें</a>
<a class="btn btn-ghost btn-block" href="{MAPS_URL}" rel="noopener" target="_blank">{ico('pin')} रास्ता देखें</a></article>
<div><div class="box note" style="margin-top:0"><h3>{ico('info')} OPD में आने से पहले</h3><ul>
<li>OPD में डेढ़ से दो घंटे या उससे अधिक प्रतीक्षा हो सकती है।</li>
<li>क्लिनिक पहुँचकर रिसेप्शन पर पंजीकरण कराएँ।</li>
<li>पुरानी रिपोर्ट, पर्चे और चल रही दवाइयाँ साथ लाएँ।</li></ul></div>
<p class="small muted" style="margin-top:14px">{E(CITY_HI)} ({SPELLINGS}), {E(DISTRICT_HI)} जिला, उत्तर प्रदेश।</p></div></div></section>
<section style="background:#fff;border-block:1px solid var(--line)"><div class="container">
<h2>इन समस्याओं के लिए {E(d['name'])} को दिखाएँ</h2>
<p class="muted">किसी भी समस्या पर टैप करें। लक्षण, कारण, घर पर देखभाल और डॉक्टर को कब दिखाना है, सब पढ़ सकते हैं।</p>
<div class="grid c3">{cards}</div></div></section>
<section><div class="container narrow"><h2>अक्सर पूछे जाने वाले प्रश्न</h2>{faq_html(faqs)}</div></section>
<section style="padding-top:0"><div class="container"><h2>आसपास के क्षेत्र</h2><div class="areas">{areas}</div>
<h3 style="margin-top:24px">दूसरे विशेषज्ञ</h3><div class="chips">{others}</div>
{cta_block(d)}</div></section>"""
    graph = [pharmacy_node(), website_node(), physician_node(d),
             {"@type": "MedicalWebPage", "@id": u(f"/{d['slug']}/#webpage"), "url": u(f"/{d['slug']}/"), "name": SPEC_TITLE[k].format(name=d["name"]),
              "isPartOf": {"@id": WEB_ID}, "inLanguage": "hi-IN", "about": {"@id": u(f"/{d['slug']}/#physician")}, "dateModified": BUILD_DATE,
              "mainEntity": {"@id": u(f"/{d['slug']}/#physician")}},
             crumb_node([("होम", "/"), ("डॉक्टर और OPD", "/doctors/"), (m["label"], f"/{d['slug']}/")]), faq_node(faqs)]
    desc = {
        "ortho": f"बड़हलगंज, गोरखपुर में हड्डी रोग विशेषज्ञ {d['name']} ({d['quals']}) की OPD, प्रत्येक रविवार सुबह 10:30 से। कमर, घुटना, गर्दन, कंधे का दर्द और चोट।",
        "skin": f"बड़हलगंज, गोरखपुर में त्वचा रोग विशेषज्ञ {d['name']} ({d['quals']}) की OPD, प्रत्येक गुरुवार दोपहर 2-5 बजे। बाल झड़ना, दाद-खाज, मुंहासे, एलर्जी।",
        "ent": f"बड़हलगंज, गोरखपुर में ENT (नाक-कान-गला) विशेषज्ञ {d['name']} की OPD, प्रत्येक शुक्रवार दोपहर 2-5 बजे। कान दर्द, गला, साइनस, सुनने की कमी।",
    }[k]
    write(f"/{d['slug']}/", layout(title=SPEC_TITLE[k].format(name=d["name"]), desc=desc, path=f"/{d['slug']}/", body=body, graph=graph,
                                  active="doctors", wa_text=f"नमस्ते, मुझे {d['name']} की OPD ({d['day_hi']}) के बारे में जानकारी चाहिए।"))
    PAGES.append(f"/{d['slug']}/")


def page_conditions_hub():
    groups = []
    for k in ("ortho", "skin", "ent"):
        m, d = SPEC[k], DOCTORS[k]
        items = "".join(
            f'<a class="chip" data-q="{E((c["hi"] + " " + c["en"] + " " + " ".join(c["also"])).lower())}" href="{c["url"]}">{E(c["chip"])}</a>'
            for c in CONDS if c["spec"] == k)
        groups.append(f'<div class="pgroup {k}" data-group><h3><span class="badge">{ico(m["icon"])}</span>{E(m["full"])}</h3>'
                      f'<p>{E(d["name"])} · <a href="/{d["slug"]}/">OPD: {E(schedule_line(d))}</a></p><div class="chips">{items}</div></div>')
    body = f"""{crumbs([("होम", "/"), ("लक्षण और बीमारियाँ", None)])}
<div class="container phead"><h1>लक्षण और बीमारियाँ: हड्डी, त्वचा, कान-नाक-गला</h1>
<p class="lead">आम परेशानियों की सरल हिंदी जानकारी: लक्षण, कारण, घर पर देखभाल और डॉक्टर को कब दिखाना है।</p></div>
<section style="padding-top:8px"><div class="container">
<div class="search"><label class="sr" for="q">समस्या खोजें</label>{ico('search')}<input id="q" type="search" placeholder="समस्या खोजें, जैसे: कमर दर्द, hair fall, sinus" autocomplete="off"></div>
<p id="q-empty" class="hide muted">कोई परिणाम नहीं मिला। WhatsApp पर पूछें या नीचे की सूची देखें।</p>
<div class="picker">{"".join(groups)}</div>
<div class="box note"><h3>{ico('info')} ध्यान दें</h3><p style="margin:0">यह जानकारी सामान्य जागरूकता के लिए है, डॉक्टर की जाँच का विकल्प नहीं। गंभीर या अचानक बढ़ती तकलीफ़ में तुरंत अस्पताल जाएँ।</p></div>
{cta_block()}</div></section>"""
    graph = [pharmacy_node(), website_node(),
             {"@type": "CollectionPage", "@id": u("/conditions/#webpage"), "url": u("/conditions/"), "name": "लक्षण और बीमारियाँ", "isPartOf": {"@id": WEB_ID}, "inLanguage": "hi-IN", "dateModified": BUILD_DATE},
             crumb_node([("होम", "/"), ("लक्षण और बीमारियाँ", "/conditions/")]),
             {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": u(c["url"]), "name": c["hi"]} for i, c in enumerate(CONDS)]}]
    write("/conditions/", layout(
        title="लक्षण और बीमारियाँ: हड्डी, त्वचा, ENT की हिंदी जानकारी | बड़हलगंज",
        desc="कमर दर्द, घुटने का दर्द, बाल झड़ना, दाद-खाज, कान दर्द, साइनस जैसी 23 आम समस्याओं के लक्षण, कारण, घरेलू देखभाल और डॉक्टर को कब दिखाएँ।",
        path="/conditions/", body=body, graph=graph, active="cond"))
    PAGES.append("/conditions/")


def reviewed_html(c):
    r = REVIEWED.get(c["slug"])
    if not r:
        return ""
    d = DOCTORS[r[0]]
    return f'<p class="small muted">{ico("check")} चिकित्सकीय समीक्षा: {E(d["name"])}, {E(r[1])}</p>'


def page_condition(c):
    k = c["spec"]
    d, m = DOCTORS[k], SPEC[k]
    faqs = list(c["faq"]) + [(
        f"{c['hi']} के लिए बड़हलगंज में किस डॉक्टर को दिखाएँ?",
        f"{d['name']} ({d['title']}) की OPD अमर मेडिकल एजेन्सी, कॉलेज तिराहा, बड़हलगंज में {schedule_line(d)} होती है। समय अनुमानित है। अपॉइंटमेंट या जानकारी के लिए WhatsApp {WHATSAPP_DISPLAY} पर संपर्क करें।")]
    related = "".join(
        f'<a class="chip" href="{BY_SLUG[s]["url"]}">{E(BY_SLUG[s]["chip"])}</a>' for s in c["related"])
    also = ", ".join(c["also"])
    urgent = ""
    if c["urgent"]:
        urgent = (f'<div class="box urgent"><h3>{ico("alert")} तुरंत इमरजेंसी या नज़दीकी अस्पताल जाएँ</h3>{ul(c["urgent"])}'
                  f'<p class="small" style="margin:8px 0 0">आपातकाल में 112 या एम्बुलेंस 108 पर कॉल करें। OPD का इंतज़ार न करें।</p></div>')
    soon = (f'<div class="box soon"><h3>{ico("info")} जल्द OPD में दिखाएँ</h3>{ul(c["soon"])}</div>') if c["soon"] else ""
    avoid = f'<div class="box avoid"><h3>{ico("alert")} क्या न करें</h3>{ul(c["avoid"])}</div>' if c["avoid"] else ""
    title = f"{c['chip']} ({c['en_short']}): लक्षण व कब दिखाएँ | बड़हलगंज"
    if len(title) > 56:
        title = f"{c['chip']}: लक्षण, कारण व कब दिखाएँ | बड़हलगंज"
    desc = f"{c['chip']} ({c['en_short']}): लक्षण, कारण, घर पर देखभाल और कब डॉक्टर को दिखाएँ। {d['name']}, OPD बड़हलगंज में प्रत्येक {d['day_hi']}।"
    toc = ('<nav class="toc" aria-label="इस पेज पर"><a href="#symptoms">लक्षण</a><a href="#causes">कारण</a><a href="#care">घर पर देखभाल</a>'
           '<a href="#when">कब दिखाएँ</a><a href="#doctor">डॉक्टर क्या करते हैं</a><a href="#faq">प्रश्न</a></nav>')
    body = f"""{crumbs([("होम", "/"), ("लक्षण और बीमारियाँ", "/conditions/"), (m["label"], f"/{d['slug']}/"), (c["chip"], None)])}
<article class="container narrow prose">
<header class="phead"><span class="tag {d['color']}">{ico(m['icon'])} {E(m['label'])}</span>
<h1 style="margin-top:10px">{E(c['hi'])} ({E(c['en_short'])})</h1>
<p class="lead">{E(c['intro'])}</p>
<p class="also">लोग इसे इन नामों से भी खोजते हैं: {E(also)}</p>{reviewed_html(c)}
<div class="card doc" style="margin-top:6px"><div class="sched">{ico('cal')}<div><strong>{E(d['name'])}</strong>, {E(d['title'])}<small>OPD: {E(schedule_line(d))}, अमर मेडिकल एजेन्सी, बड़हलगंज</small></div></div>
<a class="btn btn-wa btn-block" href="{E(doc_wa(d))}" rel="noopener">{ico('wa')} WhatsApp पर अपॉइंटमेंट पूछें</a></div></header>
{toc}
<section id="symptoms"><h2>{E(c['hi'])} के लक्षण</h2>{ul(c['symptoms'], 'ticks')}</section>
<section id="causes"><h2>कारण: {E(c['hi'])} क्यों होता है?</h2>{ul(c['causes'], 'dots')}</section>
<section id="care"><h2>घर पर क्या करें</h2>{ul(c['care'], 'ticks')}{avoid}</section>
<section id="when"><h2>डॉक्टर को कब दिखाएँ</h2>{urgent}{soon}</section>
<section id="doctor"><h2>डॉक्टर के पास क्या होता है</h2>{ul(c['doctor'], 'dots')}</section>
<section id="faq"><h2>अक्सर पूछे जाने वाले प्रश्न</h2>{faq_html(faqs)}</section>
<section><h2>इन्हें भी पढ़ें</h2><div class="chips">{related}<a class="chip" href="/conditions/">सभी लक्षण</a></div>
<div class="box note"><h3>{ico('info')} सूचना</h3><p style="margin:0">यह जानकारी सामान्य स्वास्थ्य जागरूकता के लिए है। यह डॉक्टर की जाँच, निदान या इलाज का विकल्प नहीं है। दवा या इलाज शुरू करने या बदलने से पहले डॉक्टर या फार्मासिस्ट से सलाह लें।</p></div>
{cta_block(d, "डॉक्टर से मिलकर जाँच कराएँ")}</section>
</article>"""
    mw = {"@type": "MedicalWebPage", "@id": u(c["url"]) + "#webpage", "url": u(c["url"]), "name": title, "description": desc,
          "isPartOf": {"@id": WEB_ID}, "inLanguage": "hi-IN", "dateModified": BUILD_DATE, "publisher": {"@id": PH_ID},
          "audience": {"@type": "Patient"},
          "about": {"@type": "MedicalCondition", "name": c["en_short"], "alternateName": [c["hi"]] + c["also"],
                    "signOrSymptom": [{"@type": "MedicalSymptom", "name": s} for s in c["symptoms"]]},
          "mentions": {"@id": u(f"/{d['slug']}/#physician")}}
    if c["slug"] in REVIEWED:
        rd = DOCTORS[REVIEWED[c["slug"]][0]]
        mw["lastReviewed"] = REVIEWED[c["slug"]][1]
        mw["reviewedBy"] = {"@id": u(f"/{rd['slug']}/#physician")}
    graph = [pharmacy_node(), website_node(), physician_node(d), mw,
             crumb_node([("होम", "/"), ("लक्षण और बीमारियाँ", "/conditions/"), (m["label"], f"/{d['slug']}/"), (c["chip"], c["url"])]), faq_node(faqs)]
    write(c["url"], layout(title=title, desc=desc, path=c["url"], body=body, graph=graph, active="cond",
                           wa_text=f"नमस्ते, मुझे {d['name']} की OPD ({d['day_hi']}) के बारे में जानकारी चाहिए।"))
    PAGES.append(c["url"])


def page_medicines():
    cats = [("cat-baby", "बेबी केयर", "बच्चों की देखभाल के लिए ज़रूरी उत्पाद"), ("cat-diabetes", "डायबिटीज केयर", "ब्लड शुगर मॉनिटर और संबंधित उत्पाद"),
            ("cat-heart", "हार्ट, BP और कोलेस्ट्रॉल केयर", "हृदय स्वास्थ्य के लिए आवश्यक उत्पाद"), ("cat-vitamin", "विटामिन और सप्लिमेंट्स", "दैनिक स्वास्थ्य और प्रतिरक्षा के लिए"),
            ("cat-personal", "पर्सनल केयर", "त्वचा, बाल, मुँह की देखभाल और दैनिक उपयोग उत्पाद"), ("cat-general", "सामान्य दवाईयाँ", "बुखार, दर्द, सर्दी-खाँसी और अन्य")]
    cards = "".join(f'<div class="cat"><img src="/assets/img/{i}.webp" width="236" height="168" loading="lazy" alt=""><div>{E(n)}<br><span class="small muted" style="font-weight:400">{E(t)}</span></div></div>' for i, n, t in cats)
    more = ["बुखार और दर्द", "सर्दी-खाँसी, एलर्जी व श्वसन", "पेट, पाचन व लिवर", "हार्ट, BP व थायरॉइड", "त्वचा की देखभाल", "महिला स्वास्थ्य", "प्राथमिक उपचार", "किडनी व यूरोलॉजी",
            "न्यूरोलॉजी", "नेत्र (आँख) देखभाल", "संक्रमण", "कैंसर व स्पेशलिटी दवाइयाँ", "आयुर्वेदिक और जेनेरिक दवाएँ", "सर्जिकल सामान"]
    more_html = "".join(f"<span>{E(x)}</span>" for x in more)
    faqs = [
        ("क्या सभी प्रमुख अस्पतालों के पर्चे की दवाइयाँ मिलती हैं?",
         "गोरखपुर, बड़हलगंज, लखनऊ और वाराणसी के प्रमुख अस्पतालों और विशेषज्ञ डॉक्टरों द्वारा लिखी दवाइयाँ हमारे यहाँ उपलब्ध रहती हैं। कोई दवा न हो तो उसे तुरंत या 24 घंटे के भीतर मंगाने का हर संभव प्रयास किया जाता है।"),
        ("दवा उपलब्ध है या नहीं, कैसे पता करें?", f"WhatsApp {WHATSAPP_DISPLAY} पर दवा का नाम भेजकर पूछ सकते हैं। पर्चे की फोटो या रिपोर्ट सामान्य फ़ॉर्म में न भेजें।"),
        ("क्या बिना पर्चे के हर दवा मिल जाती है?", "नहीं। पर्चे वाली दवाइयाँ केवल लागू कानूनों और डॉक्टर के पर्चे के अनुसार ही दी जाती हैं। हम बिना डॉक्टरी देखरेख के स्वयं दवा लेने को प्रोत्साहित नहीं करते।"),
        ("दवाइयों का सामान्य स्टॉक कैसा रहता है?", "आम दवाओं का भरपूर स्टॉक रखने की कोशिश रहती है। फिर भी किसी विशेष दवा की उपलब्धता बदल सकती है, इसलिए आने से पहले पूछना बेहतर है।"),
    ]
    body = f"""{crumbs([("होम", "/"), ("दवाइयाँ", None)])}
<div class="container phead"><h1>बड़हलगंज में दवाइयाँ और हेल्थ प्रोडक्ट्स</h1>
<p class="lead">आम दवाइयाँ, OTC, बेबी केयर, डायबिटीज़ केयर, विटामिन और सर्जिकल सामान। साथ ही प्रमुख अस्पतालों के पर्चे की दवाइयाँ।</p></div>
<section style="padding-top:8px"><div class="container"><h2>लोकप्रिय श्रेणियाँ</h2><div class="cats">{cards}</div>
<h3 style="margin-top:26px">और भी उपलब्ध</h3><div class="areas">{more_html}</div>
<div class="box note"><h3>{ico('info')} दवा की जानकारी में क्या देखें</h3><ul>
<li>उपयोग: दवा किस काम आती है।</li><li>सक्रिय घटक (सॉल्ट): पैकेट पर लिखा नाम और मात्रा।</li>
<li>सावधानियाँ: गर्भावस्था, बच्चे, बुज़ुर्ग, लिवर-किडनी या एलर्जी में ध्यान।</li>
<li>संभावित दुष्प्रभाव, और डॉक्टर या फार्मासिस्ट से कब पूछें।</li></ul></div></div></section>
<section style="background:#fff;border-block:1px solid var(--line)"><div class="container narrow"><h2>अक्सर पूछे जाने वाले प्रश्न</h2>{faq_html(faqs)}
<div class="box note"><h3>{ico('info')} सावधानी</h3><p style="margin:0">यहाँ दी गई जानकारी सामान्य है। किसी भी दवा का उपयोग डॉक्टर या फार्मासिस्ट की सलाह से ही करें। उत्पादों की उपलब्धता और कीमत बदल सकती है।</p></div></div></section>
<div class="container">{cta_block(None, "दवा उपलब्ध है या नहीं, पूछें")}</div>"""
    graph = [pharmacy_node(), website_node(),
             {"@type": "WebPage", "@id": u("/medicines/#webpage"), "url": u("/medicines/"), "name": "दवाइयाँ और हेल्थ प्रोडक्ट्स", "isPartOf": {"@id": WEB_ID}, "inLanguage": "hi-IN", "dateModified": BUILD_DATE},
             crumb_node([("होम", "/"), ("दवाइयाँ", "/medicines/")]), faq_node(faqs)]
    write("/medicines/", layout(
        title="बड़हलगंज में दवाइयाँ और हेल्थ प्रोडक्ट्स | अमर मेडिकल एजेन्सी",
        desc="बड़हलगंज, गोरखपुर में आम दवाइयाँ, OTC, बेबी केयर, डायबिटीज़ केयर, विटामिन और प्रमुख अस्पतालों के पर्चे की दवाइयाँ। उपलब्धता WhatsApp पर पूछें।",
        path="/medicines/", body=body, graph=graph, active="meds"))
    PAGES.append("/medicines/")


def page_location():
    landmarks = [("इंडियन ओवरसीज बैंक", "50 मीटर (1 मिनट)"), ("नेशनल इंटर कॉलेज", "250 मीटर (2 मिनट)"), ("बस स्टैंड (बाईपास)", "500 मीटर (2 मिनट)"),
                 ("ब्लॉक कार्यालय (गोला रोड)", "1.5 किमी (4 मिनट)"), ("मुक्तिपथ", "2.5 किमी (5 मिनट)")]
    lm = "".join(f"<li><span>{E(a)}</span><span>{E(b)}</span></li>" for a, b in landmarks)
    bands = [("0–5 किमी, नज़दीकी क्षेत्र", ["बड़हलगंज", "दोहरीघाट"]),
             ("5–15 किमी, आसपास के कस्बे और बाजार", ["सौंखोर", "झुमिला बाजार", "गोठा", "हाटा बाजार", "कपारवार घाट", "कूरी बाजार", "खड़ेसरी", "खर्कौली", "मोहम्मदपुर", "महुला डगरा", "जोत खजुहान", "कंदुपट्टी", "जंगल डोमरडिला", "मदनपुर", "बरांव", "रौतपार", "रसूलपुर", "सिधोरा", "बघाड़", "पिपरसंडी", "लखुआ पाकड़"]),
             ("15–30 किमी, प्रमुख कस्बे", ["गोला बाजार", "गगहा", "अमिला बाजार", "घोसी", "धुरियापार", "उरुवा बाजार", "बरहज"]),
             ("30–40 किमी, दूर के प्रमुख कस्बे", ["कौड़ीराम", "बेलघाट", "बांसगांव", "मऊ", "रुद्रपुर", "खजनी", "सिकरीगंज"])]
    bands_html = "".join(f'<h3 style="margin-top:18px">{E(t)}</h3><div class="areas">{"".join(f"<span>{E(x)}</span>" for x in xs)}</div>' for t, xs in bands)
    body = f"""{crumbs([("होम", "/"), ("लोकेशन", None)])}
<div class="container phead"><h1>अमर मेडिकल एजेन्सी का पता और लोकेशन, बड़हलगंज</h1>
<p class="lead">कॉलेज तिराहा, बड़हलगंज का एक प्रमुख और पहचाने जाने वाला स्थान। {E(CITY_HI)} ({SPELLINGS}), गोरखपुर।</p></div>
<section style="padding-top:8px"><div class="container where">
<div class="card"><dl class="facts">
<div><dt>{ico('pin')} पता</dt><dd>{E(ADDRESS_HI)}</dd></div>
<div><dt>{ico('clock')} दुकान का समय</dt><dd>{E(HOURS_HI)}<br><span class="small muted">डॉक्टर OPD का समय अलग है, देखें: <a href="/doctors/">डॉक्टर और OPD</a></span></dd></div>
<div><dt>{ico('wa')} WhatsApp</dt><dd><a href="{wa()}" rel="noopener">{WHATSAPP_DISPLAY}</a></dd></div>
<div><dt>{ico('phone')} आपातकालीन संपर्क</dt><dd>{EMERGENCY_PHONE_DISPLAY} <span class="small muted">(केवल आपातकाल हेतु)</span></dd></div></dl>
<div class="btns" style="margin-top:16px"><a class="btn btn-brand btn-block" href="{MAPS_URL}" rel="noopener" target="_blank">{ico('pin')} Google Maps पर रास्ता पाएँ</a></div></div>
<div class="card"><h2 style="font-size:1.25rem">पास के स्थान</h2><ul class="landmarks">{lm}</ul>
<ul class="trust" style="margin-top:14px"><li>{ico('check')}<span>मुख्य तिराहे पर स्थित, पहचानना आसान</span></li><li>{ico('check')}<span>दुकान के सामने और पास में वाहन पार्किंग</span></li></ul></div></div></section>
<section style="background:#fff;border-block:1px solid var(--line)"><div class="container"><h2>आसपास के क्षेत्रों से दूरी</h2>{bands_html}</div></section>
<div class="container">{cta_block()}</div>"""
    graph = [pharmacy_node(), website_node(),
             {"@type": "ContactPage", "@id": u("/location/#webpage"), "url": u("/location/"), "name": "पता और लोकेशन", "isPartOf": {"@id": WEB_ID}, "inLanguage": "hi-IN", "about": {"@id": PH_ID}, "dateModified": BUILD_DATE},
             crumb_node([("होम", "/"), ("लोकेशन", "/location/")])]
    write("/location/", layout(
        title="अमर मेडिकल एजेन्सी का पता, लोकेशन और समय | कॉलेज तिराहा, बड़हलगंज",
        desc="कॉलेज तिराहा, कॉलेज रोड, बड़हलगंज, गोरखपुर (273402)। दुकान का समय रोज़ सुबह 7:30 से रात 10 बजे, Google Maps रास्ता और पास के स्थान।",
        path="/location/", body=body, graph=graph, active="loc"))
    PAGES.append("/location/")


def page_about():
    reviews = [("रमेश यादव", "बड़हलगंज", "अमर मेडिकल एजेंसी पर दवाओं की विस्तृत रेंज उपलब्ध रहती है और लगभग सभी दवाएं बहुत ही आसानी से उपलब्ध हो जाती हैं। जब भी कोई दवा उपलब्ध नहीं होती है तो हमने देखा है कि दवाओं को तुरंत ही या अगले दिन तक मंगवा देते हैं, जो हमारे लिए बहुत अच्छी सुविधा है।"),
               ("पूजा सिंह", "गोला", "बच्चों की दवाइयाँ और बेबी केयर प्रोडक्ट्स के लिए यही हमारी पहली पसंद है। यहाँ सही सलाह भी मिलती है और व्यवहार बहुत अच्छा है। साथ ही घर के बुजुर्गों से संबंधित हर तरीके की दवा बड़ी आसानी से उपलब्ध हो जाती है, चाहे वह गोरखपुर के डॉक्टर की लिखी हुई हो या लखनऊ की।")]
    rev = "".join(f'<figure class="card" style="margin:0"><blockquote style="margin:0 0 10px">“{E(t)}”</blockquote><figcaption class="small muted"><strong>{E(n)}</strong>, {E(p)}</figcaption></figure>' for n, p, t in reviews)
    body = f"""{crumbs([("होम", "/"), ("हमारे बारे में", None)])}
<div class="container phead"><h1>हमारे बारे में: 44 वर्षों का भरोसा, एक नई शुरुआत</h1>
<p class="lead">{E(NAME_HI)}, {E(ADDRESS_SHORT_HI)} में स्थित एक विश्वसनीय मेडिकल स्टोर है, जहाँ असली दवाइयाँ, हेल्थ प्रोडक्ट्स और सही जानकारी व मार्गदर्शन मिलता है।</p></div>
<section style="padding-top:8px"><div class="container about">
<div class="ph"><img src="/assets/img/raj-dubey.webp" width="480" height="770" alt="{E(PHARMACIST)}, संचालक एवं फार्मासिस्ट" fetchpriority="high"></div>
<div><h2>हमारी कहानी</h2>
<p>बड़हलगंज (गोला रोड) में 44 वर्षों से अधिक समय से आपकी स्वास्थ्य सेवाओं में तत्पर 'अमर मेडिकल स्टोर' की सफलता और आपके भरोसे के बाद, वर्ष 2026 में हमारी दूसरी शाखा 'अमर मेडिकल एजेन्सी' ने कॉलेज तिराहा, बड़हलगंज में अपना संचालन शुरू किया।</p>
<h3>अनुभवी नेतृत्व</h3>
<p>इस शाखा के संचालक <strong>{E(PHARMACIST)}</strong> अनुभवी और प्रशिक्षित फार्मासिस्ट हैं। बड़हलगंज में शुरुआत से पहले उन्होंने गोरखपुर AIIMS के समीप अपना फार्मेसी स्टोर सफलतापूर्वक संचालित किया। इससे भी पूर्व वे पारिवारिक प्रतिष्ठान 'अमर मेडिकल स्टोर' (गोला रोड) में सेवा दे चुके हैं।</p></div></div></section>
<section style="background:#fff;border-block:1px solid var(--line)"><div class="container"><h2>हमारी सेवाएँ और विशेषताएँ</h2><div class="grid c2">
<div class="card"><h3>विस्तृत रेंज</h3><p style="margin:0">एलोपैथिक, आयुर्वेदिक, जेनेरिक दवाएँ, OTC उत्पाद, हेल्थ सप्लीमेंट्स और सर्जिकल वस्तुएँ।</p></div>
<div class="card"><h3>प्रमुख अस्पतालों की दवाएँ</h3><p style="margin:0">AIIMS (गोरखपुर), BRD मेडिकल कॉलेज (गोरखपुर), SGPGI (लखनऊ), KGMU (लखनऊ), BHU (वाराणसी) तथा अन्य अस्पतालों और विशेषज्ञों की लिखी दवाओं की उपलब्धता हमारी प्राथमिकता है।</p></div>
<div class="card"><h3>गुणवत्ता और भरोसा</h3><p style="margin:0">100% असली व अधिकृत रिटेल दवाइयाँ (कोल्ड-स्टोरेज / तापमान-नियंत्रित), उचित मूल्य पर।</p></div>
<div class="card"><h3>विशेषज्ञ डॉक्टरों की OPD</h3><p style="margin:0">हड्डी, त्वचा और ENT विशेषज्ञ हर हफ्ते। <a href="/doctors/">OPD सारणी देखें</a>।</p></div></div></div></section>
<section><div class="container"><h2>हमारे मरीजों और ग्राहकों की राय</h2><div class="grid c2">{rev}</div></div></section>
<div class="container">{cta_block()}</div>"""
    graph = [pharmacy_node(), website_node(),
             {"@type": "AboutPage", "@id": u("/about/#webpage"), "url": u("/about/"), "name": "हमारे बारे में", "isPartOf": {"@id": WEB_ID}, "about": {"@id": PH_ID}, "inLanguage": "hi-IN", "dateModified": BUILD_DATE},
             crumb_node([("होम", "/"), ("हमारे बारे में", "/about/")])]
    write("/about/", layout(
        title="हमारे बारे में | अमर मेडिकल एजेन्सी, बड़हलगंज, 44 वर्षों का भरोसा",
        desc="44 वर्ष पुराने अमर मेडिकल स्टोर परिवार की नई शाखा। संचालक और फार्मासिस्ट Drx राज दूबे, असली दवाइयाँ और विशेषज्ञ डॉक्टरों की OPD, कॉलेज तिराहा, बड़हलगंज।",
        path="/about/", body=body, graph=graph, active="about"))
    PAGES.append("/about/")


def page_legal(key, title, path, desc):
    items = json.load(open(os.path.join(os.path.dirname(__file__), "legal.json"), encoding="utf8"))[key]
    out, inlist = [], False
    for tag, text in items:
        if tag == "h1":
            continue
        lang = "hi" if re.search(r"[ऀ-ॿ]", text) else "en"
        if tag == "li":
            if not inlist:
                out.append("<ul>"); inlist = True
            out.append(f'<li lang="{lang}">{E(text)}</li>')
            continue
        if inlist:
            out.append("</ul>"); inlist = False
        if tag in ("h2", "h3"):
            out.append(f'<h2 lang="{lang}">{E(text)}</h2>')
        else:
            out.append(f'<p lang="{lang}">{E(text)}</p>')
    if inlist:
        out.append("</ul>")
    body = f"""{crumbs([("होम", "/"), (title, None)])}
<article class="container narrow legal phead"><h1 lang="en">{E(title)}</h1>{"".join(out)}
<p class="small muted">Questions: <a href="{wa()}" rel="noopener">WhatsApp {WHATSAPP_DISPLAY}</a></p></article>"""
    graph = [pharmacy_node(), website_node(), crumb_node([("होम", "/"), (title, path)])]
    write(path, layout(title=f"{title} | {NAME_EN}", desc=desc, path=path, body=body, graph=graph))
    PAGES.append(path)


def page_404():
    body = f"""<div class="container narrow phead" style="padding-block:48px"><h1>यह पेज नहीं मिला</h1>
<p class="lead">लिंक पुराना हो सकता है। नीचे से सही जगह चुनें।</p>
<div class="chips"><a class="chip" href="/">होम</a><a class="chip" href="/doctors/">डॉक्टर और OPD</a><a class="chip" href="/conditions/">लक्षण और बीमारियाँ</a><a class="chip" href="/medicines/">दवाइयाँ</a><a class="chip" href="/location/">लोकेशन</a></div>
<p style="margin-top:24px"><a class="btn btn-wa" href="{wa()}" rel="noopener">{ico('wa')} WhatsApp पर पूछें</a></p></div>"""
    html_ = layout(title=f"पेज नहीं मिला | {NAME_HI}", desc="यह पेज उपलब्ध नहीं है।", path="/404.html", body=body, graph=[pharmacy_node()], noindex=True)
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf8") as f:
        f.write(html_)


# ------------------------------------------------------------------ machine-readable files
def md_list(items):
    return "\n".join(f"- {i}" for i in items)


def build_llms():
    lines = [
        f"# {NAME_HI} ({NAME_EN})", "",
        f"> Pharmacy and weekly specialist-doctor OPD in Barhalganj ({SPELLINGS}), Gorakhpur district, Uttar Pradesh, India, PIN {PIN}. "
        "Specialists: Orthopedics (Sundays), Dermatology (Thursdays), ENT (Fridays). Hindi-first patient-education pages on 23 common conditions.", "",
        "## Key facts (maintained by the clinic)", "",
        f"- Address: {ADDRESS_HI} (College Tiraha, College Road, Barhalganj)",
        f"- Coordinates: {GEO[0]}, {GEO[1]}",
        f"- Pharmacy hours: every day 07:30–22:00 IST",
        f"- WhatsApp (appointments & enquiries): +{WHATSAPP}",
        f"- Emergency-only phone: +{EMERGENCY_PHONE}",
        f"- Google Maps: {MAPS_URL}",
        "- Pharmacist / proprietor: Drx Raj Dubey. Branch of the 44-year-old Amar Medical Store (Gola Road, Barhalganj); this branch opened in 2026.",
        "- OPD timings are approximate; waiting time can be 1.5–2 hours or more; patients register at reception on arrival.", "",
        "## Specialist doctors (weekly OPD at College Tiraha, Barhalganj)", "",
    ]
    for k in ("ortho", "skin", "ent"):
        d = DOCTORS[k]
        lines.append(f"- [{d['name_en']} ({d['name']}), {d['title_en']}]({u('/' + d['slug'] + '/')}): {d['quals']}. OPD every {d['day_schema']}, {d['time_hi']}.")
    lines += ["", "## Site sections", "",
              f"- [Doctors & OPD schedule]({u('/doctors/')}): weekly OPD table and WhatsApp appointment enquiry",
              f"- [Symptoms & conditions index]({u('/conditions/')}): 23 patient-education pages in Hindi",
              f"- [Medicines & health products]({u('/medicines/')}): categories, hospital-prescription availability",
              f"- [Location]({u('/location/')}): address, landmarks, distances from nearby towns",
              f"- [About]({u('/about/')}): history and pharmacist", ""]
    for k in ("ortho", "skin", "ent"):
        lines.append(f"## {SPEC[k]['full']}: condition pages ({DOCTORS[k]['name_en']})\n")
        for c in CONDS:
            if c["spec"] == k:
                lines.append(f"- [{c['hi']} / {c['en']}]({u(c['url'])}): symptoms, causes, home care, red flags, when to see the doctor")
        lines.append("")
    lines += ["## Guidance for AI assistants", "",
              "- Cite the specific page URL. The site is in Hindi (Devanagari); English names are given alongside.",
              "- Content is general patient education, not diagnosis or treatment. Do not present it as a doctor's personal advice.",
              "- OPD days/times are approximate; advise users to confirm on WhatsApp before travelling.",
              "- The clinic does not claim to be the 'best' doctor/pharmacy. Do not state rankings on its behalf.",
              f"- Last updated: {BUILD_DATE}.", ""]
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf8").write("\n".join(lines))

    full = [f"# {NAME_HI} ({NAME_EN}): full text for AI systems", "",
            f"Source: {DOMAIN}. Updated {BUILD_DATE}. General patient-education content; not a substitute for medical advice. "
            f"Doctors: " + "; ".join(f"{DOCTORS[k]['name_en']} ({DOCTORS[k]['title_en']}, {schedule_line(DOCTORS[k])})" for k in DOCTORS) + f". Address: {ADDRESS_HI}. WhatsApp +{WHATSAPP}.", ""]
    for c in CONDS:
        d = DOCTORS[c["spec"]]
        full += [f"## {c['hi']} ({c['en']})", f"URL: {u(c['url'])}", f"Specialist: {d['name_en']}, {d['title_en']}; OPD {schedule_line(d)} at Amar Medical Agency, Barhalganj.",
                 f"Also searched as: {', '.join(c['also'])}", "", c["intro"], "",
                 "### लक्षण (Symptoms)", md_list(c["symptoms"]), "", "### कारण (Causes)", md_list(c["causes"]), "",
                 "### घर पर देखभाल (Home care)", md_list(c["care"]), ""]
        if c["avoid"]:
            full += ["### क्या न करें (Avoid)", md_list(c["avoid"]), ""]
        if c["urgent"]:
            full += ["### तुरंत इमरजेंसी (Urgent: go to hospital now)", md_list(c["urgent"]), ""]
        full += ["### जल्द OPD में दिखाएँ (See a doctor soon)", md_list(c["soon"]), "", "### डॉक्टर क्या करते हैं (What the doctor does)", md_list(c["doctor"]), "",
                 "### FAQ"] + [f"**{q}**\n{a}\n" for q, a in c["faq"]] + [""]
    open(os.path.join(OUT, "llms-full.txt"), "w", encoding="utf8").write("\n".join(full))


def build_static_files():
    urls = "".join(f"<url><loc>{u(p)}</loc><lastmod>{BUILD_DATE}</lastmod></url>" for p in PAGES)
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf8").write(
        "# Everyone, including search engines and AI assistants, is welcome to read this public health-information site.\n"
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {DOMAIN}/sitemap.xml\n")
    json.dump({"name": NAME_HI, "short_name": "अमर मेडिकल", "lang": "hi", "start_url": "/", "display": "standalone",
               "background_color": "#fbfaf6", "theme_color": "#0b3fa8",
               "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                         {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]},
              open(os.path.join(OUT, "manifest.webmanifest"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    open(os.path.join(OUT, "_headers"), "w").write(
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
        "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n")
    json.dump({"headers": [
        {"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"},
                                         {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                                         {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"}]},
        {"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]}],
        "trailingSlash": True},
        open(os.path.join(OUT, "vercel.json"), "w"), indent=1)


def main():
    os.makedirs(os.path.join(OUT, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "assets", "js"), exist_ok=True)
    open(os.path.join(OUT, "assets", "css", "site.css"), "w", encoding="utf8").write(CSS_TXT)
    open(os.path.join(OUT, "assets", "js", "site.js"), "w", encoding="utf8").write(JS_TXT)
    # remove previously generated pages, keep assets/
    for name in os.listdir(OUT):
        p = os.path.join(OUT, name)
        if name != "assets" and os.path.isdir(p):
            shutil.rmtree(p)
    page_home()
    page_doctors_hub()
    for k in DOCTORS:
        page_specialty(k)
    page_conditions_hub()
    for c in CONDS:
        page_condition(c)
    page_medicines()
    page_location()
    page_about()
    page_legal("privacy", "Privacy Policy", "/privacy/", "How Amar Medical Agency handles information you share through this website and WhatsApp.")
    page_legal("terms", "Terms of Use", "/terms/", "Terms of use for the Amar Medical Agency website, including medicine information, OPD timings and appointment requests.")
    page_404()
    build_static_files()
    build_llms()
    print(f"built {len(PAGES)} pages -> {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
