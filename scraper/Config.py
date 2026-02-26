"""
تعريف الدول + الأقسام + المصادر الرسمية/الرئيسية للـ scraping.
هذا الملف ليس سرياً، ويُستخدم من الـ spiders والـ pipelines.
"""
#الدول 
COUNTRIES = {
    "sa": "Saudi Arabia",
    "uk": "United Kingdom",
    "de": "Germany",
    "in": "India",
    "pk": "Pakistan",
    "id": "Indonesia",
    "cn": "China",
}
# الأقسام الموحدة
SECTIONS = {
    "traffic": "Traffic / Road Safety",
    "visa_residency": "Visa & Residency",
    "public_decency": "Public Decency & Conduct",
    "labor": "Labor & Employment",
    "food": "Food & Alcohol",
    "everyday_criminal": "Everyday Criminal Law",
}

# المصادر الرسمية لكل دولة + كل قسم
SOURCES = {
    #السعودية
        "sa": {
        # المرور
        "traffic": [
            {
                "name": "sa_boe_traffic_law",
                "type": "html",
                "base_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/85364e57-c01e-41ba-8def-a9a700f183e9/1",
                "official": True,
                "notes": "نظام المرور السعودي (النص العربي)..[web:113]",
            },
        ],
        # الإقامة والتأشيرات
        "visa_residency": [
            {
                "name": "sa_privileged_residency_law_pdf",
                "type": "html",
                "base_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/5e9762df-2b15-4e66-8cdc-aa5200f62042/1",
                "official": True,
                "notes": "Privileged Residency Permit Law (نموذج واضح لقانون إقامة للأجانب)..[web:128]",
            },
        ],
        # الآداب العامة / الذوق العام
        "public_decency": [
            {
                "name": "sa_public_decency_resolution_info",
                "type": "html",
                "base_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/3b96a591-47c8-4469-9abb-aa4700f1aa52/1",
                "official": True,
                "notes": "نظام لائحة الذوق العام (النص العربي)..[web:129]",
            },
        ],
        # العمل والعقود
        "labor": [
            {
                "name": "sa_labour_law_pdf",
                "type": "html",
                "base_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1",
                "official": True,
                "notes": "نظام العمل السعودي (النص العربي).",
            },
        ],
        # المأكولات / الغذاء
        "food": [
            {
                "name": "sa_food_violations_table",
                "type": "html",
                "base_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/9167ec51-a011-4a22-b6c3-a9a700f290f8/1",
                "official": True,
                "notes": "نظام الغذاء السعودي (النص العربي)..[web:130]",
            },
        ],
    },

    # المملكة المتحدة
     "uk": {
        "traffic": [
            {
                "name": "uk_road_traffic_act_1988",
                "type": "xml",
                "base_url": "htthttps://www.legislation.gov.uk/ukpga/1988/52/data.xml",
                "official": True,
                "notes": "Road Traffic Act 1988 – قانون مرور تاريخي يعطي صورة عن تنظيم المرور.[web:117]",
            },
        ],
        "visa_residency": [
            {
                "name": "uk_immigration_acts_pdf",
                "type": "xml",
                "base_url": "https://www.legislation.gov.uk/ukpga/1971/77/data.xml",
                "official": True,
                "notes": "Immigration Acts 1971 – مجموعة من القوانين التي تحدد إقامة الأجانب في المملكة المتحدة.[web:129]",
            },
        ],
        "public_decency": [
            {
                "name": "uk_public_order_context",
                "type": "xml",
                "base_url": "https://www.legislation.gov.uk/ukpga/1986/64/data.xml",
                "official": True,
                "notes": "Public Order Act 1986 – قانون إدارة الذوق العام في المملكة المتحدة.[web:129]",
            },
        ],
        "labor": [
            {
                "name": "uk_labour_law_portal",
                "type": "xml",
                "base_url": "https://www.legislation.gov.uk/ukpga/1996/18/data.xml",
                "official": True,
                "notes": "Labor Law Portal 1996 – بوابة للوصول إلى قوانين مثل Employment Rights Act 1996.",
            },
        ],
        "food": [
            {
                "name": "uk_food_safety_portal",
                "type": "xml",
                "base_url": "https://www.legislation.gov.uk/ukpga/1990/16/data.xml",
                "official": True,
                "notes": "بوابة للوصول إلى Food Safety Act 1990 ولوائح الغذاء.",
            },
        ]
    },
    #المانيا
   "de": {
        "traffic": [
            {
                "name": "de_traffic_portal",
                "type": "xml",
                "base_url": "https://www.gesetze-im-internet.de/stvg/xml.zip",
                "official": True,
                "notes": "مدخل لقوانين مثل Straßenverkehrs-Ordnung (StVg) لقواعد المرور.",
            },
        ],
        "visa_residency": [
            {
                "name": "de_residence_act_info",
                "type": "xml",
                "base_url": "https://www.gesetze-im-internet.de/aufenthg_2004/xml.zip",
                "official": False,
                "notes": "مدخل لقوانين مثل AufenthG 2004 لقواعد الإقامة.",
            },
        ],
        "public_decency": [
            {
                "name": "de_public_order_placeholder",
                "type": "xml",
                "base_url": "https://www.gesetze-im-internet.de/stgb/xml.zip",
                "official": True,
                "notes": "مدخل لقوانين مثل Öffentliches Ordnungsgesetz (StGB) لقواعد السلوك العام.",
            },
        ],
        "labor": [
            {
                "name": "de_labour_law_portal",
                "type": "xml",
                "base_url": "https://www.gesetze-im-internet.de/bgb/xml.zip",
                "official": True,
                "notes": "مدخل لقوانين العمل مثل Arbeitszeitgesetz وغيره.",
            },
        ],
        "food": [
            {
                "name": "de_food_regulation_portal",
                "type": "xml",
                "base_url": "https://www.gesetze-im-internet.de/lfgb/xml.zip",
                "official": True,
                "notes": "مدخل لقوانين مثل Landwirtschaftliche Gesetzgebung (LFGB) لقواعد الغذاء.",
            }
        ],
    },

"""
الدول اللتي اسفل لم يتم تثبيت و تاكيد مصادرها
"""

    # الهند
     "in": {
        "traffic": [
            {
                "name": "in_motor_vehicles_act_pdf",
                "type": "pdf",
                "base_url": "https://www.indiacode.nic.in/bitstream/123456789/21540/1/motor_vehicle_act.pdf",
                "official": True,
                "notes": "Motor Vehicles Act 1988 – القانون المركزي الأساسي للمرور.[web:114][web:118]",
            },
        ],
        "visa_residency": [
            {
                "name": "in_immigration_foreigners_act_pdf",
                "type": "pdf",
                "base_url": "https://www.indiacode.nic.in/bitstream/123456789/21918/1/A2025-13.pdf",
                "official": True,
                "notes": "Immigration and Foreigners Act, 2025 – إطار شامل للتأشيرات والإقامة.[web:122][web:124]",
            },
        ],
        "public_decency": [
            {
                "name": "in_public_order_placeholder",
                "type": "html",
                "base_url": "https://www.indiacode.nic.in/",
                "official": True,
                "notes": "لاحقاً نستخرج نصوصاً من IPC أو قوانين النظام العام.",
            },
        ],
        "labor": [
            {
                "name": "in_labour_law_portal",
                "type": "html",
                "base_url": "https://www.indiacode.nic.in/",
                "official": True,
                "notes": "مدخل لمجموعة قوانين العمل مثل قانون عقود العمل والحد الأدنى للأجور.",
            },
        ],
        "food": [
            {
                "name": "in_food_safety_portal",
                "type": "html",
                "base_url": "https://www.indiacode.nic.in/",
                "official": True,
                "notes": "نستخدمه للوصول لقانون Food Safety and Standards Act.",
            },
        ]
    },


    # باكستان
    "pk": {
        "traffic": [
            {
                "name": "pk_punjab_traffic_rules",
                "type": "html",
                "base_url": "https://mtwds.punjabpolice.gov.pk/traffic-rules",
                "official": True,
                "notes": "قواعد المرور من شرطة البنجاب – تعليمات عملية للسائقين.[web:116]",
            },
        ],
        "visa_residency": [
            {
                "name": "pk_visa_info_placeholder",
                "type": "html",
                "base_url": "https://www.pakistan.gov.pk/",
                "official": True,
                "notes": "Placeholder لمصادر رسمية حول التأشيرات؛ نحدد قانوناً/لوائح محددة لاحقاً.",
            },
        ],
        "public_decency": [
            {
                "name": "pk_public_order_placeholder",
                "type": "html",
                "base_url": "https://punjablaws.gov.pk/",
                "official": True,
                "notes": "مدخل لقوانين النظام العام في إقليم البنجاب.",
            },
        ],
        "labor": [
            {
                "name": "pk_labour_law_portal",
                "type": "html",
                "base_url": "https://punjablaws.gov.pk/",
                "official": True,
                "notes": "نستخرج منه قوانين العمل الباكستانية/الإقليمية.",
            },
        ],
        "food": [
            {
                "name": "pk_food_safety_portal",
                "type": "html",
                "base_url": "https://punjablaws.gov.pk/",
                "official": True,
                "notes": "لاحقاً نختار لوائح سلامة الأغذية.",
            },
        ],
    },


    # إندونيسيا
 "id": {
        "traffic": [
            {
                "name": "id_road_traffic_law_pdf",
                "type": "pdf",
                "base_url": "https://dishub.malangkota.go.id/wp-content/uploads/sites/16/2016/05/Undang-Undang-No.-22-tahun-2009-Tentang-Lalulintas.pdf",
                "official": True,
                "notes": "Law No. 22 of 2009 on Road Traffic and Transportation.[web:115][web:119]",
            },
        ],
        "visa_residency": [
            {
                "name": "id_immigration_law_pdf",
                "type": "pdf",
                "base_url": "https://www.peraturan.go.id/files2/uu-no-6-tahun-2011_terjemah.pdf",
                "official": True,
                "notes": "Law No. 6 of 2011 on Immigration.[web:130]",
            },
        ],
        "public_decency": [
            {
                "name": "id_public_order_placeholder",
                "type": "html",
                "base_url": "https://peraturan.go.id/eng",
                "official": True,
                "notes": "مدخل للبحث عن قوانين السلوك في الأماكن العامة.",
            },
        ],
        "labor": [
            {
                "name": "id_labour_law_portal",
                "type": "html",
                "base_url": "https://peraturan.go.id/eng",
                "official": True,
                "notes": "نستخرج منه قوانين العمل الإندونيسية.",
            },
        ],
        "food": [
            {
                "name": "id_food_law_portal",
                "type": "html",
                "base_url": "https://peraturan.go.id/eng",
                "official": True,
                "notes": "مدخل لقوانين سلامة الغذاء.",
            },
        ]
    },

    # الصين
    "cn": {
        "traffic": [
            {
                "name": "cn_road_traffic_safety_law",
                "type": "html",
                "base_url": "http://english.www.gov.cn/archive/laws_regulations/2014/08/23/content_281474983042477.htm",
                "official": True,
                "notes": "Road Traffic Safety Law of the PRC (Official English Version).",
            },
        ],
        "visa_residency": [
            {
                "name": "cn_exit_entry_admin_law",
                "type": "html",
                "base_url": "http://english.www.gov.cn/archive/laws_regulations/2014/08/23/content_281474983042515.htm",
                "official": True,
                "notes": "Exit and Entry Administration Law of the PRC.",
            },
        ],
        "public_decency": [
            {
                "name": "cn_public_order_placeholder",
                "type": "html",
                "base_url": "http://english.www.gov.cn/archive/laws_regulations/",
                "official": True,
                "notes": "مدخل لقوانين العقوبات الإدارية والأمن العام (Public Security Administration Punishments Law).",
            },
        ],
        "labor": [
            {
                "name": "cn_labour_law_portal",
                "type": "html",
                "base_url": "http://english.www.gov.cn/archive/laws_regulations/",
                "official": True,
                "notes": "Labour Law of the PRC.",
            },
        ],
        "food": [
            {
                "name": "cn_food_safety_law",
                "type": "html",
                "base_url": "http://english.www.gov.cn/archive/laws_regulations/2014/08/23/content_281474983042473.htm",
                "official": True,
                "notes": "Food Safety Law of the PRC.",
            },
        ]
    }
}

# ─── WorldLII كمصدر احتياطي عام ───
WORLDLII_FALLBACK = {
    "sa": "https://www.worldlii.org/sa",
    "uk": "https://www.worldlii.org/uk",
    "de": "https://www.worldlii.org/de",
    "in": "https://www.worldlii.org/in",
    "pk": "https://www.worldlii.org/pk",
    "id": "https://www.worldlii.org/id",
    "cn": "https://www.worldlii.org/cn",
}



def get_source(country: str, section: str, include_fallback: bool = True) -> list:
    """
    إرجاع مصادر الرسمية للـ scraping حسب الدولة و القسم , WorldLII كا مصدر احتياطي.
    مثال :
     sources = await get_source("sa", "traffic")
    """
    sources = SOURCES.get(country, {}).get(section, [])

    if include_fallback and country in WORLDLII_FALLBACK:
         sources = sources + [
            {
                "name": f"{country}_worldlii_fallback",
                "type": "html",
                "base_url": WORLDLII_FALLBACK[country],
                "official": True,
                "priority": 99,  # دائماً آخر خيار
                "notes": "WorldLII fallback – يُستخدم فقط إذا فشلت المصادر الرسمية.",
            }
        ]

    return sources
