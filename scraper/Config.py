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
                "name": "sa_privileged_residency_law",
                "type": "html",
                "base_url": "https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/5e9762df-2b15-4e66-8cdc-aa5200f62042/1",
                "official": True,
                "notes": "Privileged Residency Permit Law (نظام الإقامة المميزة).",
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
                "name": "sa_labor_law_pdf",
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
                "base_url": "https://www.legislation.gov.uk/ukpga/1988/52/data.xml",
                "official": True,
                "notes": "Road Traffic Act 1988 – قانون مرور تاريخي يعطي صورة عن تنظيم المرور.[web:117]",
            },
        ],
        "visa_residency": [
            {
                "name": "uk_immigration_acts_1971",
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
                "name": "uk_labor_law_portal",
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
                "name": "de_traffic_law",
                "type": "html",
                "base_url": "https://www.gesetze-im-internet.de/stvg/BJNR004370909.html",
                "official": True,
                "notes": "نظام المرور الألماني (StVG) .",
            },
        ],
        "visa_residency": [
            {
                "name": "de_residence_act",
                "type": "html",
                "base_url": "https://www.gesetze-im-internet.de/aufenthg_2004/BJNR195010004.html",
                "official": True,
                "notes": "نظام الإقامة الألماني (AufenthG)",
            },
        ],
        "public_decency": [
            {
                "name": "de_criminal_code",
                "type": "html",
                "base_url": "https://www.gesetze-im-internet.de/stgb/BJNR001270871.html",
                "official": True,
                "target_sections": ["§ 123","§ 124","§ 125","§ 131","§ 166","§ 167","§ 167a","§ 168","§ 181a","§ 183","§ 183a","§ 184","§ 185","§ 186","§ 187","§ 199","§ 223","§ 224","§ 242","§ 303","§ 315b","§ 315c","§ 315d","§ 324","§ 325a"], # أمثلة لمواد تتعلق بالسلوك العام والآداب 
                "notes": "القانون الجنائي الألماني (StGB) - بالتحديد مواد السلوك العام والآداب فقط.",
            },
        ],
        "labor": [
            {
                "name": "de_labor_law",
                "type": "html",
                "base_url": "https://www.gesetze-im-internet.de/bgb/BJNR001950896.html",
                "official": True,
                "target_sections": ["§ 611", "§ 611a", "§ 612", "§ 612a", "§ 613", "§ 613a", "§ 614", "§ 615", "§ 616", "§ 617", "§ 618", "§ 619", "§ 619a", "§ 620", "§ 621", "§ 622", "§ 623", "§ 624", "§ 625", "§ 626", "§ 627", "§ 628", "§ 629", "§ 630","§ 631","§ 632", "§ 633","§ 634", "§ 635","§ 636","§ 637","§ 638","§ 639","§ 640","§ 641","§ 642","§ 643","§ 644","§ 645","§ 646","§ 647","§ 648","§ 649","§ 650"], #  المواد تتعلق بالوظائف والدوام 
                "notes": "القانون المدني الألماني (BGB) - قسم علاقات العمل.",
            },
        ],
        "food": [
            {
                "name": "de_food_law",
                "type": "html",
                "base_url": "https://www.gesetze-im-internet.de/lfgb/BJNR261810005.html",
                "official": True,
                "notes": "قانون الغذاء والأعلاف الألماني (LFGB).",
            }
        ],
    },

"""
الدول اللتي اسفل لم يتم تثبيت و تاكيد مصادرها (الا الصين)
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
                "name": "in_labor_law_portal",
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
                "name": "pk_labor_law_portal",
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
                "name": "id_labor_law_portal",
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
                "base_url": "http://www.npc.gov.cn/zgrdw/englishnpc/Law/2007-12/11/content_1383213.htm",
                "official": True,
                "notes": "Road Traffic Safety Law of the PRC (Official English Version - NPC).",
            },
        ],
        "visa_residency": [
            {
                "name": "cn_exit_entry_admin_law",
                "type": "html",
                "base_url": "http://www.npc.gov.cn/zgrdw/englishnpc/Law/2013-02/20/content_1754084.htm",
                "official": True,
                "notes": "Exit and Entry Administration Law of the PRC (2013).",
            },
        ],
        "public_decency": [
            {
                "name": "cn_public_security_punishments_law",
                "type": "html",
                "base_url": "http://www.npc.gov.cn/zgrdw/englishnpc/Law/2007-12/11/content_1383215.htm",
                "official": True,
                "notes": "Public Security Administration Punishments Law (covers public conduct & order).",
            },
        ],
        "labor": [
            {
                "name": "cn_labor_law",
                "type": "html",
                "base_url": "http://www.npc.gov.cn/zgrdw/englishnpc/Law/2007-12/12/content_1383754.htm",
                "official": True,
                "notes": "Labour Law of the PRC.",
            },
        ],
        "food": [
            {
                "name": "cn_food_safety_law",
                "type": "html",
                "base_url": "http://www.npc.gov.cn/zgrdw/englishnpc/Law/2011-02/15/content_1620635.htm",
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
