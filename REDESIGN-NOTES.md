# Amar Medical Agency: redesigned website

Static, mobile-first, Hindi-first site. 34 pages, no framework, no tracking. Output is the `docs/` folder.

```
python3 tools/build.py      # regenerate docs/ from tools/config.py + tools/content_*.py
python3 tools/validate.py   # checks links, JSON-LD, titles, duplicate ids, sitemap
```

Edit facts (phone, doctors, OPD days) only in `tools/config.py`. Edit medical text in `tools/content_ortho.py`, `content_derm.py`, `content_ent.py`. Never edit `docs/` by hand.

## What is in it

| Section | URL | Purpose |
|---|---|---|
| Home | `/` | Symptom-first picker, "today's OPD" (auto-highlights today), open/closed status, WhatsApp CTA |
| Doctors hub | `/doctors/` | Weekly OPD table, 3 doctors, WhatsApp booking form, FAQ |
| Specialty pages | `/orthopedic-doctor-barhalganj/`, `/skin-doctor-barhalganj/`, `/ent-doctor-barhalganj/` | Target "skin/bone/ENT doctor in Barhalganj" searches |
| Conditions | `/conditions/` + 23 pages | Symptoms, causes, home care, what NOT to do, red flags (urgent vs soon), FAQ |
| Others | `/medicines/ /location/ /about/ /privacy/ /terms/` | |
| Machine-readable | `sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt`, JSON-LD on every page | Search + AI assistants |

JSON-LD per page: `Pharmacy` (with geo, hours, area served), `Physician` (+ specialty, OPD day), `MedicalWebPage` + `MedicalCondition` + `MedicalSymptom`, `FAQPage`, `BreadcrumbList`.

## Honest SEO expectations

- No one can guarantee rank #1. Realistic targets: "skin/bone/ENT doctor Barhalganj" (and the spellings Badhalganj/Badalganj) plus the long-tail symptom searches. "Best doctor in Gorakhpur" is dominated by city hospitals; this site can win some long-tail Gorakhpur-district queries but not that head term.
- The site never claims "best". It answers the "best doctor" query honestly (qualifications, specialty, OPD) because misleading medical claims hurt both trust and ranking.
- `llms.txt` is a convention, not a ranking factor, and no major AI product has confirmed using it. What actually feeds AI answers is clean crawlable HTML, schema, consistent name/address/phone everywhere, and third-party mentions (Google Business Profile, Practo, Justdial).
- Health content is "YMYL". It ranks far better when a named doctor reviews it. See step 1 below.

## Before you launch (needs the owner / doctors)

1. **Doctor review of all 23 condition pages** (drafted as patient education, not reviewed). When a doctor approves a page, add it to `REVIEWED` in `config.py`. The page then shows "reviewed by" and emits `reviewedBy` in schema.
2. Dr. B. P. Singh's qualification reads "MBBS (ENT)", which is not a standard specialist degree. Confirm (MS/DLO/DNB ENT?). His photo is 176px wide; supply a larger one. Consider adding registration numbers for all doctors.
3. Phones: WhatsApp 88875 27372 is the main action. 96956 56542 is labelled "emergency only" on the old site, so no Call button is shown. Set `PROMOTE_CALL_BUTTON = True` only if it may take normal calls. Use exactly the same number and address on Google Business Profile.
4. No consultation fees are shown (the old meta description promised them). Add if wanted. Add drug licence and GST numbers to the footer.
5. Omitted on purpose: the testimonial from "Arvind Gupta" (says he is a long-time customer of a branch that opened in 2026; clarify), and any "गुप्त रोग" pages (need the doctor's wording and a privacy-first design).
6. **Not migrated:** the 418-item medicine catalogue from the old site. It includes prescription brands (e.g. tramadol combinations); decide a compliance-safe OTC-only version first. `/medicines/` currently lists categories and FAQs.
7. Privacy Policy and Terms are copied verbatim from the old site (dated 12 Oct 2026; Privacy mentions Vercel hosting). Update if hosting changes.

## Deploy

- **Vercel (keeps your current domain setup):** import this repo, Output Directory = `docs`, no build command.
- **GitHub Pages:** Settings, Pages, branch + `/docs` folder; then repoint DNS.
- Then: fix `www.amarmedicalagency.in` (currently HTTP 522), verify the domain in Google Search Console and submit `sitemap.xml`, and check Cloudflare, Security, Bots: make sure AI crawlers are not blocked and the "managed robots.txt" is not overriding `docs/robots.txt`.
- The old sitemap pointed at `amar-sooty.vercel.app`; this one uses `amarmedicalagency.in`.

## Next steps worth doing

- Google Business Profile: website link, doctors/services, weekly OPD, Q&A, reviews (biggest local-ranking lever).
- Short Hindi videos per condition (with doctor consent, no patient identifiers), embedded on the matching page with `VideoObject` schema. This ties your YouTube/Reels work to search.
