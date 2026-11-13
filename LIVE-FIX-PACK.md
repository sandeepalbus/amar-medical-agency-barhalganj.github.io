# Fix pack for the live pages (Next.js / v0)

Applies to `https://amarmedicalagency.in/doctors/orthopaedics` and `/doctors/orthopaedics/knee-pain`. Decision recorded: Sunday OPD = **"प्रत्येक रविवार, सुबह 10:30 बजे से"** (no end time) everywhere.

## 1. Text to remove or replace (visible to patients today)

| Where | Remove / replace | With |
|---|---|---|
| Hub, booking box | `यह केवल फॉर्म का preview है। लाइव WhatsApp booking अभी कनेक्ट नहीं है।` | `अपॉइंटमेंट की पुष्टि क्लिनिक से उपलब्धता की जाँच के बाद ही होगी।` (same line already used on the knee page) |
| Hub, booking button | `अपॉइंटमेंट बुक करें` (does nothing) | `WhatsApp पर अपॉइंटमेंट पूछें`, link: `https://wa.me/918887527372?text=नमस्ते, मुझे डॉ. अविनाश सिंह की OPD (रविवार) के बारे में जानकारी चाहिए।` (URL-encode the text) |
| Hub, "विश्वसनीय स्वास्थ्य स्रोत" paragraph | `इन links का उद्देश्य ... Google penalty ... आवश्यक हैं।` | `ये लिंक पाठकों को आगे पढ़ने के लिए हैं। यह जानकारी सामान्य स्वास्थ्य शिक्षा के लिए है।` |
| Hub, sources list | link `Google Search Central — Helpful, Reliable, People-First Content` | **Delete it.** Keep WHO, MedlinePlus, NHS. A Google SEO page is not a health source. |
| Hub, OPD card | `सुबह 10:30 बजे से दोपहर 2:00 बजे तक` | `प्रत्येक रविवार, सुबह 10:30 बजे से` |
| Hub and knee page, doctor line | `डॉ. अविनाश सिंह \| Orthopedic Surgeon` | `डॉ. अविनाश सिंह, हड्डी, जोड़ एवं नस रोग विशेषज्ञ \| MBBS, MS (Orthopedics)` (as on /doctors) |
| Hub H1 | `हड्डियों और जोड़ों की समस्याएँ: लक्षण एवं स्वास्थ्य जानकारी` | `हड्डियों और जोड़ों की समस्याएँ: लक्षण, कारण और बड़हलगंज में OPD` |
| Hub `<title>` | `Orthopaedics \| हड्डियों और जोड़ों की स्वास्थ्य जानकारी \| अमर मेडिकल एजेन्सी` | `हड्डी और जोड़ों का दर्द: लक्षण, कारण, OPD | बड़हलगंज` |
| Hub meta description | current | `कमर, घुटने, गर्दन और कंधे के दर्द, स्लिप डिस्क, साइटिका और चोट की सरल हिंदी जानकारी। हड्डी रोग विशेषज्ञ डॉ. अविनाश सिंह, प्रत्येक रविवार, बड़हलगंज।` |

Use both spellings in body text once ("Orthopaedics / ऑर्थोपेडिक"). Most Indian searches use "orthopedic".

## 2. Add 4 FAQs to the hub (visible text + schema must match)

**बड़हलगंज में हड्डी के डॉक्टर कब बैठते हैं?**  डॉ. अविनाश सिंह (MBBS, MS Orthopedics) प्रत्येक रविवार सुबह 10:30 बजे से अमर मेडिकल एजेन्सी, कॉलेज तिराहा, बड़हलगंज में OPD करते हैं। समय अनुमानित है, आने से पहले WhatsApp पर पुष्टि कर लें।

**कमर दर्द, घुटने के दर्द और स्लिप डिस्क में कौन सा डॉक्टर दिखाएँ?**  ये हड्डी, जोड़ और रीढ़ की समस्याएँ हैं। इनके लिए ऑर्थोपेडिक विशेषज्ञ (हड्डी रोग विशेषज्ञ) को दिखाया जाता है।

**चोट लगने के बाद 'हड्डी बैठाने वाले' के पास जाना ठीक है?**  अगर फ्रैक्चर की आशंका हो तो पहले X-ray और डॉक्टर की जाँच ज़रूरी है। जोर-जबरदस्ती की खिंचाई से नस या खून की नली को नुकसान हो सकता है।

**OPD में कितना इंतज़ार करना पड़ता है?**  OPD में डेढ़ से दो घंटे या उससे अधिक प्रतीक्षा हो सकती है। क्लिनिक पहुँचकर रिसेप्शन पर पंजीकरण कराएँ।

## 3. Make the symptom list useful (28 items, 1 link)

Don't create 28 thin pages: Google treats that as low-value scaled content. Link only items that get a real page (about 800 words like knee-pain), and leave the rest as text or merge them:

| Hub item(s) | Page to build | Draft text already written |
|---|---|---|
| कमर में दर्द | `/doctors/orthopaedics/back-pain` | yes: `tools/content_ortho.py` → `kamar-dard-back-pain` |
| स्लिप डिस्क | `/slip-disc` | yes |
| कमर से पैर तक दर्द (साइटिका), झनझनाहट/सुन्नपन | `/sciatica` | yes |
| गर्दन में दर्द, गर्दन से हाथ तक दर्द | `/neck-pain` | yes |
| कंधे में दर्द, फ्रोजन शोल्डर | `/shoulder-pain` | yes |
| हड्डियों की कमजोरी | `/osteoporosis` | yes |
| मोच, लिगामेंट, खेल की चोट, खिंचाव | `/sprain-sports-injury` | yes |
| ऑस्टियोआर्थराइटिस, जोड़ों में सूजन, सुबह अकड़न | merge into knee-pain (or one `/arthritis` page) | partly |
| टेनिस एल्बो, कलाई, एड़ी, टखना | one page each only when the doctor supplies content | no |
| फ्रैक्चर, फॉलो-अप | one page, **needs the doctor's wording** | no |

Every new page: same OPD line, 3+ links to related pages, FAQs, and the red-flag box. The hub currently links only `/doctors/orthopaedics/knee-pain`.

## 4. JSON-LD (validated JSON; paste as shown)

Home page (`/`): put the `Pharmacy` node (first node below) once. On the hub page use the whole graph:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Pharmacy",
      "@id": "https://amarmedicalagency.in/#pharmacy",
      "name": "अमर मेडिकल एजेन्सी",
      "alternateName": "Amar Medical Agency",
      "url": "https://amarmedicalagency.in/",
      "description": "बड़हलगंज (गोरखपुर) में दवा की दुकान, जहाँ हड्डी, त्वचा और ENT के विशेषज्ञ डॉक्टरों की साप्ताहिक OPD भी होती है। / Pharmacy with weekly orthopedic, dermatology and ENT OPD in Barhalganj, Gorakhpur.",
      "image": [
        "https://amarmedicalagency.in/assets/img/og-default.jpg",
        "https://amarmedicalagency.in/assets/img/storefront-d.webp"
      ],
      "logo": "https://amarmedicalagency.in/assets/img/icon-512.png",
      "telephone": "+919695656542",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "कॉलेज तिराहा, कॉलेज रोड",
        "addressLocality": "बड़हलगंज",
        "addressRegion": "उत्तर प्रदेश",
        "postalCode": "273402",
        "addressCountry": "IN"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": 26.2871209,
        "longitude": 83.505208
      },
      "hasMap": "https://maps.app.goo.gl/hsi9sp5Y5zM8nQV86",
      "openingHoursSpecification": [
        {
          "@type": "OpeningHoursSpecification",
          "dayOfWeek": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
          ],
          "opens": "07:30",
          "closes": "22:00"
        }
      ],
      "areaServed": [
        {
          "@type": "Place",
          "name": "बड़हलगंज"
        },
        {
          "@type": "Place",
          "name": "दोहरीघाट"
        },
        {
          "@type": "Place",
          "name": "सौंखोर"
        },
        {
          "@type": "Place",
          "name": "झुमिला बाजार"
        },
        {
          "@type": "Place",
          "name": "गोठा"
        },
        {
          "@type": "Place",
          "name": "हाटा बाजार"
        },
        {
          "@type": "Place",
          "name": "कपारवार घाट"
        },
        {
          "@type": "Place",
          "name": "कूरी बाजार"
        },
        {
          "@type": "Place",
          "name": "गोला बाजार"
        },
        {
          "@type": "Place",
          "name": "गगहा"
        },
        {
          "@type": "Place",
          "name": "अमिला बाजार"
        },
        {
          "@type": "Place",
          "name": "घोसी"
        },
        {
          "@type": "Place",
          "name": "धुरियापार"
        },
        {
          "@type": "Place",
          "name": "उरुवा बाजार"
        },
        {
          "@type": "Place",
          "name": "बरहज"
        },
        {
          "@type": "Place",
          "name": "कौड़ीराम"
        },
        {
          "@type": "Place",
          "name": "बेलघाट"
        },
        {
          "@type": "Place",
          "name": "बांसगांव"
        },
        {
          "@type": "Place",
          "name": "मऊ"
        },
        {
          "@type": "Place",
          "name": "खजनी"
        },
        {
          "@type": "Place",
          "name": "सिकरीगंज"
        }
      ],
      "contactPoint": [
        {
          "@type": "ContactPoint",
          "contactType": "customer support",
          "telephone": "+918887527372",
          "availableLanguage": [
            "Hindi",
            "English"
          ]
        }
      ],
      "employee": {
        "@type": "Person",
        "name": "Raj Dubey",
        "jobTitle": "Pharmacist and Proprietor"
      },
      "sameAs": [
        "https://www.facebook.com/amarmedicalagency",
        "https://www.instagram.com/amarmedicalagency.bg/",
        "https://youtube.com/@amarmedicalagency_bg",
        "https://maps.app.goo.gl/hsi9sp5Y5zM8nQV86"
      ]
    },
    {
      "@type": "Physician",
      "@id": "https://amarmedicalagency.in/doctors/orthopaedics#physician",
      "name": "Dr. Avinash Singh",
      "alternateName": "डॉ. अविनाश सिंह",
      "description": "Orthopedic Specialist (Bone, Joint & Spine) holding OPD at Amar Medical Agency, College Tiraha, Barhalganj, Gorakhpur every Sunday.",
      "medicalSpecialty": "Musculoskeletal",
      "url": "https://amarmedicalagency.in/doctors/orthopaedics",
      "image": "https://amarmedicalagency.in/assets/img/dr-avinash-singh.webp",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "कॉलेज तिराहा, कॉलेज रोड",
        "addressLocality": "बड़हलगंज",
        "addressRegion": "उत्तर प्रदेश",
        "postalCode": "273402",
        "addressCountry": "IN"
      },
      "location": {
        "@id": "https://amarmedicalagency.in/#pharmacy"
      },
      "openingHoursSpecification": {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": "Sunday",
        "opens": "10:30"
      },
      "availableLanguage": [
        "Hindi",
        "English"
      ],
      "knowsAbout": [
        "Back Pain",
        "Slipped (Herniated) Disc",
        "Neck Pain",
        "Sciatica",
        "Knee Pain",
        "Osteoporosis",
        "Shoulder Pain",
        "Sports Injury, Sprain & Strain"
      ]
    },
    {
      "@type": "MedicalWebPage",
      "@id": "https://amarmedicalagency.in/doctors/orthopaedics#webpage",
      "url": "https://amarmedicalagency.in/doctors/orthopaedics",
      "name": "हड्डियों और जोड़ों की समस्याएँ: लक्षण, कारण और बड़हलगंज में OPD",
      "inLanguage": "hi-IN",
      "dateModified": "2026-11-13",
      "publisher": {
        "@id": "https://amarmedicalagency.in/#pharmacy"
      },
      "mainEntity": {
        "@id": "https://amarmedicalagency.in/doctors/orthopaedics#physician"
      },
      "audience": {
        "@type": "Patient"
      }
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "होम",
          "item": "https://amarmedicalagency.in/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "डॉक्टर और OPD",
          "item": "https://amarmedicalagency.in/doctors"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "हड्डी और जोड़",
          "item": "https://amarmedicalagency.in/doctors/orthopaedics"
        }
      ]
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "बड़हलगंज में हड्डी के डॉक्टर कब बैठते हैं?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "डॉ. अविनाश सिंह (MBBS, MS Orthopedics) प्रत्येक रविवार सुबह 10:30 बजे से अमर मेडिकल एजेन्सी, कॉलेज तिराहा, बड़हलगंज में OPD करते हैं। समय अनुमानित है, आने से पहले WhatsApp पर पुष्टि कर लें।"
          }
        },
        {
          "@type": "Question",
          "name": "कमर दर्द, घुटने के दर्द और स्लिप डिस्क में कौन सा डॉक्टर दिखाएँ?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "ये हड्डी, जोड़ और रीढ़ की समस्याएँ हैं। इनके लिए ऑर्थोपेडिक विशेषज्ञ (हड्डी रोग विशेषज्ञ) को दिखाया जाता है।"
          }
        },
        {
          "@type": "Question",
          "name": "चोट लगने के बाद 'हड्डी बैठाने वाले' के पास जाना ठीक है?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "अगर फ्रैक्चर की आशंका हो तो पहले X-ray और डॉक्टर की जाँच ज़रूरी है। जोर-जबरदस्ती की खिंचाई से नस या खून की नली को नुकसान हो सकता है।"
          }
        },
        {
          "@type": "Question",
          "name": "OPD में कितना इंतज़ार करना पड़ता है?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "OPD में डेढ़ से दो घंटे या उससे अधिक प्रतीक्षा हो सकती है। क्लिनिक पहुँचकर रिसेप्शन पर पंजीकरण कराएँ।"
          }
        }
      ]
    }
  ]
}
```

Knee-pain page:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "MedicalWebPage",
      "@id": "https://amarmedicalagency.in/doctors/orthopaedics/knee-pain#webpage",
      "url": "https://amarmedicalagency.in/doctors/orthopaedics/knee-pain",
      "name": "घुटनों में दर्द: कारण, लक्षण और सावधानियाँ",
      "inLanguage": "hi-IN",
      "dateModified": "2026-11-13",
      "publisher": {
        "@id": "https://amarmedicalagency.in/#pharmacy"
      },
      "audience": {
        "@type": "Patient"
      },
      "about": {
        "@type": "MedicalCondition",
        "name": "Knee pain",
        "alternateName": [
          "घुटनों में दर्द",
          "knee pain",
          "knee osteoarthritis"
        ],
        "signOrSymptom": [
          {
            "@type": "MedicalSymptom",
            "name": "चलते समय घुटने में दर्द"
          },
          {
            "@type": "MedicalSymptom",
            "name": "सीढ़ियाँ चढ़ने-उतरने में परेशानी"
          },
          {
            "@type": "MedicalSymptom",
            "name": "सुबह उठने पर घुटनों में अकड़न"
          },
          {
            "@type": "MedicalSymptom",
            "name": "घुटने में सूजन"
          },
          {
            "@type": "MedicalSymptom",
            "name": "घुटना मोड़ने या सीधा करने में कठिनाई"
          },
          {
            "@type": "MedicalSymptom",
            "name": "घुटने में क्लिक या कट-कट की आवाज"
          },
          {
            "@type": "MedicalSymptom",
            "name": "घुटने में कमजोरी या अस्थिरता"
          },
          {
            "@type": "MedicalSymptom",
            "name": "गर्माहट, लालिमा या छूने पर दर्द"
          }
        ]
      },
      "mentions": {
        "@id": "https://amarmedicalagency.in/doctors/orthopaedics#physician"
      }
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "होम",
          "item": "https://amarmedicalagency.in/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "डॉक्टर और OPD",
          "item": "https://amarmedicalagency.in/doctors"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "हड्डी और जोड़",
          "item": "https://amarmedicalagency.in/doctors/orthopaedics"
        },
        {
          "@type": "ListItem",
          "position": 4,
          "name": "घुटनों में दर्द",
          "item": "https://amarmedicalagency.in/doctors/orthopaedics/knee-pain"
        }
      ]
    }
  ]
}
```

Do not add `reviewedBy` until Dr. Avinash Singh has actually reviewed the page; then add `"lastReviewed": "YYYY-MM-DD", "reviewedBy": {"@id": "https://amarmedicalagency.in/doctors/orthopaedics#physician"}`.

## 5. Next.js (App Router) code

`app/layout.tsx`: set the base URL once.
```tsx
export const metadata = { metadataBase: new URL("https://amarmedicalagency.in") };
```

`components/json-ld.tsx`
```tsx
export function JsonLd({ data }: { data: object }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}
    />
  );
}
```

`app/doctors/orthopaedics/page.tsx` (same pattern on `knee-pain/page.tsx` with its own text)
```tsx
export const metadata = {
  title: "हड्डी और जोड़ों का दर्द: लक्षण, कारण, OPD | बड़हलगंज",
  description: "कमर, घुटने, गर्दन और कंधे के दर्द, स्लिप डिस्क, साइटिका और चोट की सरल हिंदी जानकारी। हड्डी रोग विशेषज्ञ डॉ. अविनाश सिंह, प्रत्येक रविवार, बड़हलगंज।",
  alternates: { canonical: "/doctors/orthopaedics" },
  openGraph: { type: "website", locale: "hi_IN", siteName: "अमर मेडिकल एजेन्सी",
    url: "/doctors/orthopaedics", images: [{ url: "/og-default.jpg", width: 1200, height: 630 }] },
};
// inside the component:  <JsonLd data={hubGraph} />   (hubGraph = the JSON above)
```
Copy `docs/assets/img/og-default.jpg` from this repo to `public/og-default.jpg`.

`app/sitemap.ts` (delete any hand-written `public/sitemap.xml` that lists amar-sooty.vercel.app, otherwise the two conflict)
```ts
import type { MetadataRoute } from "next";
const base = "https://amarmedicalagency.in";
const paths = ["/", "/doctors", "/doctors/orthopaedics", "/doctors/orthopaedics/knee-pain", "/doctors/dermatology", "/doctors/ent", "/medicines", "/location", "/about", "/privacy", "/terms"];
export default function sitemap(): MetadataRoute.Sitemap {
  return paths.map((p) => ({ url: base + p, lastModified: "2026-11-13" }));
}
```
Equivalent static `sitemap.xml` if you prefer a file:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://amarmedicalagency.in/</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://amarmedicalagency.in/doctors</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://amarmedicalagency.in/doctors/orthopaedics</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://amarmedicalagency.in/doctors/orthopaedics/knee-pain</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://amarmedicalagency.in/doctors/dermatology</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://amarmedicalagency.in/doctors/ent</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://amarmedicalagency.in/medicines</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://amarmedicalagency.in/location</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://amarmedicalagency.in/about</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://amarmedicalagency.in/privacy</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://amarmedicalagency.in/terms</loc><lastmod>2026-11-13</lastmod></url>
</urlset>
```
`robots.txt`:
```
User-agent: *
Allow: /

Sitemap: https://amarmedicalagency.in/sitemap.xml
```
Also check Cloudflare, Security, Bots: AI crawler blocking and "managed robots.txt" can override this file.

## 6. Prompt to paste into v0

> On the Next.js site, make these changes. (1) On /doctors/orthopaedics remove the sentence "यह केवल फॉर्म का preview है…", turn the booking button into a link to https://wa.me/918887527372 with a URL-encoded Hindi message, delete the "Google Search Central" source link and the paragraph mentioning "Google penalty", and change the OPD time to "प्रत्येक रविवार, सुबह 10:30 बजे से" on every page. (2) Add per-page `metadata` (title, description, canonical via `alternates`, openGraph with /og-default.jpg) and set `metadataBase` to https://amarmedicalagency.in in the root layout. (3) Add a `JsonLd` component and render the JSON-LD I provide on the hub, the knee-pain page and the home page. (4) Replace the sitemap with `app/sitemap.ts` using the domain https://amarmedicalagency.in. (5) Add the 4 FAQs as `<details>` accordions on the hub. (6) Make the symptom chips on the hub into links, but only for pages that exist.

## 7. Still needs the owner

Doctor review before more pages go live, higher-resolution photo and qualification check for Dr. B. P. Singh, and a decision on which symptom pages to write first (section 3).
