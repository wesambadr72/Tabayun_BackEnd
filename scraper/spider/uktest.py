import requests
from lxml import etree

url = "https://www.legislation.gov.uk/ukpga/1988/52/data.xml"

def test_uk_xml():
    print(f"📡 Fetching data from UK Legislation: {url}")
    # إضافة Headers لتجنب أي حظر
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    # تحويل النص إلى XML tree
    tree = etree.fromstring(response.content)
    
    # تعريف الـ namespaces الشائعة في legislation.gov.uk
    ns = {
        'ukl': 'http://www.legislation.gov.uk/namespaces/legislation',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    
    # 1. استخراج عنوان القانون الرئيسي (من Dublin Core metadata)
    main_title = tree.xpath("//dc:title/text()", namespaces=ns)
    law_name = main_title[0].strip() if main_title else "N/A"
    print(f"📜 Law Title: {law_name}\n")
    
    # 2. استخراج الأقسام الرئيسية فقط (تجنب الملاحق والجداول الفرعية)
    # نركز على P1group الموجودة داخل Body القانون فقط
    # نستخدم مساراً أدق للوصول للمواد الـ 197 الأساسية
    articles = tree.xpath("//ukl:Body//ukl:P1group", namespaces=ns)
    
    print(f"✅ Found {len(articles)} sections in Body.\n")
    
    for i, art in enumerate(articles):
        # استخراج اسم الباب (Part)
        part_title = art.xpath("ancestor::ukl:Part/ukl:Title/text()", namespaces=ns)
        current_part = part_title[0].strip() if part_title else "General Provisions"

        # استخراج عنوان المادة (Title) - قد يكون في P1group أو في أول P1
        section_title = art.xpath("./ukl:Title/text()", namespaces=ns)
        if not section_title:
            section_title = art.xpath(".//ukl:Title/text()", namespaces=ns)
        
        final_title = section_title[0].strip() if section_title else "Untitled Section"
        
        # استخراج رقم المادة (Pnumber) - مكانه الدقيق هو داخل P1
        section_number = art.xpath("./ukl:P1/ukl:Pnumber/text()", namespaces=ns)
        if not section_number:
            section_number = art.xpath(".//ukl:Pnumber/text()", namespaces=ns)
            
        final_number = section_number[0].strip() if section_number else f"S.{i+1}"
        
        # استخراج النص (جمع كل نصوص الفقرات P1para)
        body_parts = art.xpath(".//ukl:Text//text()", namespaces=ns)
        body = " ".join([t.strip() for t in body_parts if t.strip()])
        
        # دمج المعلومات في العنوان
        display_title = f"{law_name} - {current_part} - {final_title}"

        # طباعة أول 3 وأخر 3 للتأكد من المدى (1 إلى 197)
        if i < 3 or i >= len(articles) - 3:
            print(f"--- Section {i+1} [Official No: {final_number}] ---")
            print(f"artical number: {final_number}")
            print(f"🏷️ Full Title: {display_title}")
            print(f"📝 Text Snippet: {body[:150]}...")
            print("-" * 30)
        
        if i == 2:
            print("... (skipping middle sections) ...\n")

if __name__ == "__main__":
    test_uk_xml()