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
                "type": "pdf",
                "base_url": "https://laws.boe.gov.sa/Files/Download/?attId=484cc8af-575e-45e5-ab8f-adbb010e982c",
                "official": True,
                "notes": "Privileged Residency Permit Law (نموذج واضح لقانون إقامة للأجانب)..[web:128]",
            },
        ],
        # الآداب العامة / الذوق العام
        "public_decency": [
            {
                "name": "sa_public_decency_resolution_info",
                "type": "html",
                "base_url": "https://www.loc.gov/item/global-legal-monitor/2019-11-04/saudi-arabia-legislation-enacted-on-regulating-public-decency/",
                "official": False,
                "notes": "مقال مكتبة الكونغرس يشرح قرار الذوق العام رقم 444؛ نستخدمه كبوابة لتحديد النص الرسمي لاحقاً.[web:132]",
            },
        ],
        # العمل والعقود
        "labor": [
            {
                "name": "sa_labour_law_pdf",
                "type": "pdf",
                "base_url": "https://beoe.gov.pk/files/legal-framework/labor-laws/Saudi-Labour-Law.pdf",
                "official": False,
                "notes": "نسخة مترجمة من نظام العمل السعودي (من موقع باكستاني رسمي لوزارة شؤون المغتربين). مفيدة للمقارنات.[web:133]",
            },
        ],
        # المأكولات / الغذاء
        "food": [
            {
                "name": "sa_food_violations_table",
                "type": "html",
                "base_url": "https://momah.gov.sa/en/node/15200",
                "official": True,
                "notes": "مقال عن جدول مخالفات أنظمة الغذاء المحدث من وزارة الشؤون البلدية والإسكان بالتعاون مع هيئة الغذاء والدواء.[web:134]",
            },
        ],
    },

    # المملكة المتحدة
     "uk": {
        "traffic": [
            {
                "name": "uk_road_traffic_act_1960",
                "type": "html",
                "base_url": "https://www.legislation.gov.uk/ukpga/Eliz2/8-9/16/enacted",
                "official": True,
                "notes": "Road Traffic Act 1960 – قانون مرور تاريخي يعطي صورة عن تنظيم المرور.[web:117]",
            },
        ],
        "visa_residency": [
            {
                "name": "uk_immigration_acts_pdf",
                "type": "pdf",
                "base_url": "https://assets.publishing.service.gov.uk/media/5a82b4bced915d74e3403267/immigrationacts.pdf",
                "official": True,
                "notes": "وثيقة تجمع أهم Immigration Acts في المملكة المتحدة.[web:129]",
            },
        ],
        "public_decency": [
            {
                "name": "uk_public_order_context",
                "type": "html",
                "base_url": "https://www.legislation.gov.uk/",
                "official": True,
                "notes": "بوابة عامة؛ لاحقاً نختار منها قوانين مثل Public Order Act و indecency/offences in public.",
            },
        ],
        "labor": [
            {
                "name": "uk_labour_law_portal",
                "type": "html",
                "base_url": "https://www.legislation.gov.uk/",
                "official": True,
                "notes": "نستخدمه للوصول إلى قوانين مثل Employment Rights Act 1996 لاحقاً.",
            },
        ],
        "food": [
            {
                "name": "uk_food_safety_portal",
                "type": "html",
                "base_url": "https://www.legislation.gov.uk/",
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
                "type": "html",
                "base_url": "https://www.gesetze-im-internet.de/",
                "official": True,
                "notes": "مدخل لقوانين مثل Straßenverkehrs-Ordnung (StVO) لقواعد المرور.[web:92]",
            },
        ],
        "visa_residency": [
            {
                "name": "de_residence_act_info",
                "type": "html",
                "base_url": "https://germanystudy.net/german-residence-act-aufenthaltsgesetz-aufenthg/",
                "official": False,
                "notes": "مقال يعرض Residence Act (AufenthG) مع نص القانون؛ نستخدمه كنقطة دخول.[web:127][web:136]",
            },
        ],
        "public_decency": [
            {
                "name": "de_public_order_placeholder",
                "type": "html",
                "base_url": "https://www.gesetze-im-internet.de/",
                "official": True,
                "notes": "لاحقاً نختار نصوصاً من القوانين الجنائية أو التنظيمية المتعلقة بالسلوك في الأماكن العامة.",
            },
        ],
        "labor": [
            {
                "name": "de_labour_law_portal",
                "type": "html",
                "base_url": "https://www.gesetze-im-internet.de/",
                "official": True,
                "notes": "بوابة للوصول إلى قوانين العمل مثل Arbeitszeitgesetz وغيره.",
            },
        ],
        "food": [
            {
                "name": "de_food_regulation_portal",
                "type": "html",
                "base_url": "https://www.gesetze-im-internet.de/",
                "official": True,
                "notes": "منها نستخرج القوانين المتعلقة بسلامة الغذاء.",
            },
        ]
    },

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
