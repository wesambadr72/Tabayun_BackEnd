import requests
from parsel import Selector

# الرابط المباشر للنسخة الكاملة HTML
url = "https://www.gesetze-im-internet.de/stvg/BJNR004370909.html"

def test_de_html_css():
    print(f"📡 Fetching HTML data from German Legislation: {url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding 
    except Exception as e:
        print(f"❌ Failed to fetch URL: {e}")
        return

    # استخدام parsel.Selector لمحاكاة Scrapy تماماً
    sel = Selector(text=response.text)
    
    # 1. استخراج عنوان القانون الرئيسي باستخدام CSS Selector
    law_title = sel.css("span.jnlangue::text").get() or "German Law"
    print(f"📜 Law Title: {law_title.strip()}\n")
    
    # 2. استخراج الأقسام بناءً على الهيكل المنظم في الصورة
    # كل مادة مغلفة في div class="jnnorm"
    articles = sel.css("div.jnnorm")
    
    print(f"✅ Found {len(articles)} sections using the 'jnnorm' container structure.\n")
    
    # عرض أول 3 مواد وآخر مادة للتأكد
    indices_to_show = [0, 1, 2, len(articles)-1]
    
    for i, art in enumerate(articles):
        # استخراج رقم المادة وعنوانها من الرأس (jnheader)
        final_number = art.css("span.jnenbez::text").get() or f"S.{i+1}"
        final_title = art.css("span.jnentitel::text").get() or ""
        
        # استخراج النص من الفقرات (jurAbsatz)
        body_parts = art.css("div.jurAbsatz ::text").getall()
        body = "\n".join([t.strip() for t in body_parts if t.strip()])

        if i in indices_to_show:
            print(f"--- Section {i+1} ---")
            print(f"📍 Number: {final_number.strip()}")
            print(f"🏷️ Title: {final_title.strip()}")
            print(f"📝 Text Snippet: {body[:200]}...")
            print("-" * 30)
        
        if i == 2:
            print(f"... (skipping {len(articles)-4} sections) ...\n")

if __name__ == "__main__":
    test_de_html_css()