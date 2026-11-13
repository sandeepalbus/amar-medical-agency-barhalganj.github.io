# -*- coding: utf-8 -*-
"""Single source of truth for NAP (name/address/phone), doctors and OPD days.

Everything here was taken from the live site (amarmedicalagency.in) as of 2026-11-13.
Anything marked TODO is NOT known and must be confirmed with the owner before launch.
"""

DOMAIN = "https://amarmedicalagency.in"
BUILD_DATE = "2026-11-13"

NAME_HI = "अमर मेडिकल एजेन्सी"
NAME_EN = "Amar Medical Agency"
TAGLINE = "बड़हलगंज का भरोसा"

STREET_HI = "कॉलेज तिराहा, कॉलेज रोड"
CITY_HI = "बड़हलगंज"
DISTRICT_HI = "गोरखपुर"
STATE_HI = "उत्तर प्रदेश"
PIN = "273402"
ADDRESS_HI = f"{STREET_HI}, {CITY_HI}, {DISTRICT_HI}, {STATE_HI} – {PIN}"
ADDRESS_SHORT_HI = f"{STREET_HI}, {CITY_HI}, {DISTRICT_HI}"
GEO = (26.2871209, 83.505208)  # from the owner's Google Maps link
MAPS_URL = "https://maps.app.goo.gl/hsi9sp5Y5zM8nQV86"

WHATSAPP = "918887527372"
WHATSAPP_DISPLAY = "88875 27372"
# Shown on the live site as "(For Emergency Only)". Kept as emergency contact only.
EMERGENCY_PHONE = "919695656542"
EMERGENCY_PHONE_DISPLAY = "96956 56542"
# Flip to True ONLY if the owner confirms this number may receive normal calls.
PROMOTE_CALL_BUTTON = False

OPEN_TIME, CLOSE_TIME = "07:30", "22:00"  # every day
HOURS_HI = "प्रत्येक दिन सुबह 7:30 बजे – रात 10:00 बजे"

FACEBOOK = "https://www.facebook.com/amarmedicalagency"
INSTAGRAM = "https://www.instagram.com/amarmedicalagency.bg/"
YOUTUBE = "https://youtube.com/@amarmedicalagency_bg"

PHARMACIST = "Drx राज दूबे"

# Spelling variants people actually type (used once, naturally, on key pages)
SPELLINGS = "Barhalganj / Badhalganj / Badalganj"

# day: schema.org day name, js: JS getDay() index
DOCTORS = {
    "ortho": {
        "key": "ortho",
        "slug": "orthopedic-doctor-barhalganj",
        "name": "डॉ. अविनाश सिंह",
        "name_en": "Dr. Avinash Singh",
        "title": "हड्डी, जोड़ एवं नस रोग विशेषज्ञ",
        "title_en": "Orthopedic Specialist (Bone, Joint & Spine)",
        "specialty_hi": "हड्डी और जोड़",
        "quals": "MBBS, MS (Orthopedics)",
        "inst": "BRD मेडिकल कॉलेज, गोरखपुर",
        "day_hi": "रविवार",
        "day_schema": "Sunday",
        "js_day": 0,
        "time_hi": "सुबह 10:30 बजे से",
        "opens": "10:30",
        "closes": None,  # live site gives only a start time
        "photo": "dr-avinash-singh.webp",
        "photo_size": (480, 640),
        "schema_specialty": "Musculoskeletal",
        "color": "ortho",
    },
    "skin": {
        "key": "skin",
        "slug": "skin-doctor-barhalganj",
        "name": "डॉ. सुप्रिया के.जी.",
        "name_en": "Dr. Supriya K.G.",
        "title": "त्वचा, गंजापन एवं गुप्त रोग विशेषज्ञ",
        "title_en": "Dermatologist (Skin, Hair & Venereology)",
        "specialty_hi": "त्वचा और बाल",
        "quals": "MBBS, MD (Skin & VD) | Gold Medalist",
        "inst": "BRD मेडिकल कॉलेज, गोरखपुर",
        "day_hi": "गुरुवार",
        "day_schema": "Thursday",
        "js_day": 4,
        "time_hi": "दोपहर 2:00 बजे – 5:00 बजे",
        "opens": "14:00",
        "closes": "17:00",
        "photo": "dr-supriya-kg.webp",
        "photo_size": (480, 576),
        "schema_specialty": "Dermatology",
        "color": "skin",
    },
    "ent": {
        "key": "ent",
        "slug": "ent-doctor-barhalganj",
        "name": "डॉ. बी. पी. सिंह",
        "name_en": "Dr. B. P. Singh",
        "title": "नाक, कान एवं गला रोग विशेषज्ञ",
        "title_en": "ENT Specialist (Ear, Nose & Throat)",
        "specialty_hi": "नाक, कान और गला",
        # TODO(owner): "MBBS (ENT)" is not a standard specialist degree (usually MS/DLO/DNB ENT). Confirm.
        "quals": "MBBS (ENT) | Ear, Nose, Throat",
        "inst": "राजकीय मेडिकल कॉलेज, देवरिया",
        "day_hi": "शुक्रवार",
        "day_schema": "Friday",
        "js_day": 5,
        "time_hi": "दोपहर 2:00 बजे – 5:00 बजे",
        "opens": "14:00",
        "closes": "17:00",
        "photo": "dr-bp-singh.webp",
        "photo_size": (176, 224),  # TODO(owner): low-res photo, supply a larger one
        "schema_specialty": "Otolaryngologic",
        "color": "ent",
    },
}

# Pages where a doctor has reviewed the medical content: {condition_slug: ("ortho", "2026-11-20")}.
# Leave EMPTY until a doctor has actually reviewed. Filling it shows "reviewed by" + schema.
REVIEWED = {}

AREAS = [
    "बड़हलगंज", "दोहरीघाट", "सौंखोर", "झुमिला बाजार", "गोठा", "हाटा बाजार",
    "कपारवार घाट", "कूरी बाजार", "गोला बाजार", "गगहा", "अमिला बाजार", "घोसी",
    "धुरियापार", "उरुवा बाजार", "बरहज", "कौड़ीराम", "बेलघाट", "बांसगांव", "मऊ",
    "खजनी", "सिकरीगंज",
]
