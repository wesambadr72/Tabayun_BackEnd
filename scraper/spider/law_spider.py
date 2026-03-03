import scrapy
from scraper.Config import get_source
from scraper.items import LawItem
import re

class LawSpider(scrapy.Spider):
    name = "law_spider"
    
    def __init__(self, country="sa", section="traffic", *args, **kwargs):
        super(LawSpider, self).__init__(*args, **kwargs)
        self.country = country
        self.section = section
        
    def start_requests(self):
        # 1. جلب المصادر من Config.py
        sources = get_source(self.country, self.section)
        
        if not sources:
            self.logger.warning(f"No sources found for country={self.country}, section={self.section}")
            return
        # 2. توليد الطلبات
        for source in sources:
            yield scrapy.Request(
                url=source["base_url"],
                callback=self.parse,
                meta={"source_info": source}
            )
    #من هنا يبدأ عملية استخراج البيانات
    def parse(self, response):
        source_info = response.meta["source_info"]
        self.logger.info(f"Scraping {source_info['name']} ({source_info['base_url']})")
        
        # 1. التوجيه بناءً على نوع المصدر 
        if source_info.get("type") == "xml":
            yield from self.parse_xml_law(response)
            return
        else:
            yield from self.parse_law_detail(response)



    def parse_law_detail(self, response):
        source_info = response.meta.get("source_info", {})
        law_title = response.css("h1::text, span.jnlangue::text").get() or response.css("title::text").get()
        if not law_title:
            law_title = f"Law from {self.country} - {self.section}"

        # 1. دعم الهيكل الألماني (German Structure - jnnorm)
        de_articles = response.css("div.jnnorm")
        if de_articles:
            self.logger.info(f"Found {len(de_articles)} German articles (jnnorm).")
            for article in de_articles:
                raw_article_number = article.css("span.jnenbez::text").get() 
                article_number = raw_article_number.replace("§","").strip() if raw_article_number else "N/A"
                article_title = article.css("span.jnentitel::text").get() or ""
                texts = article.css("div.jurAbsatz ::text").getall()
                article_body = "\n".join([t.strip() for t in texts if t.strip()])
                
                if not article_number and not article_body:
                    continue

                final_num = article_number.strip() if article_number else "N/A"
                full_title = f"{law_title.strip()} - {final_num} {article_title.strip()}".strip()
                
                yield LawItem(
                    title=full_title,
                    original_text=article_body,
                    country=self.country,
                    category=self.section,
                    article_number=final_num,
                    source_url=response.url,
                    date_scraped="now"
                )
            return

        # 2. دعم الهيكل السعودي (Saudi Structure)
        articles = response.css("div.article_item")
        
        if articles:
            self.logger.info(f"Found {len(articles)} structured articles via CSS selectors.")
            
            for article in articles:
                # استخراج عنوان المادة (h3)
                article_title = article.css("h3::text").get()
                if not article_title:
                    continue # تخطي إذا لم يوجد عنوان
                
                article_title = article_title.strip()
                
                # استخراج النص: قد يكون داخل div.HTMLContainer أو p مباشرة
                # نستخدم xpath لجمع كل النصوص داخل هذه الحاوية باستثناء العنوان نفسه
                # الطريقة: نأخذ كل النصوص التي تأتي بعد العنوان h3
                
                # تجميع النصوص من الفقرات والحاويات
                texts = article.css("div.HTMLContainer ::text, p ::text").getall()
                
                # تنظيف النصوص من عبارات التعديل والهوامش
                cleaned_texts = []
                for t in texts:
                    t = t.strip()
                    if not t:
                        continue
                    # استبعاد عبارات التعديل الشائعة
                    if "عُدلت هذه المادة" in t or "بموجب المرسوم الملكي" in t or "وتاريخ" in t and "هـ" in t:
                        continue
                    cleaned_texts.append(t)
                
                article_body = "\n".join(cleaned_texts)
                
                # تنظيف النص
                if not article_body:
                     # محاولة بديلة: أحياناً النص يكون مباشراً داخل الـ div
                     body_texts = article.xpath('text()').getall()
                     article_body = "\n".join([t.strip() for t in body_texts if t.strip()])
                #عنوان المادة مع نصها
                full_article_text = f"{article_title}\n{article_body}"

                yield LawItem(
                    title=f"{main_title.strip()} - {article_title}",
                    original_text=article_body if article_body else " ",
                    country=self.country,
                    category=self.section,
                    article_number=article_title,
                    source_url=f"{response.url}",
                    date_scraped="now"
                )
            return 

    def parse_xml_law(self, response):
        """معالجة القوانين بصيغة XML (مثل UK Legislation) مع دعم الأبواب والأرقام الدقيقة"""

        source_info = response.meta.get("source_info", {})
        
        # إزالة الـ namespaces لتسهيل البحث بـ XPath~
        # نستخدم التعريفات الصريحة لضمان الدقة
        ns = {
            'ukl': 'http://www.legislation.gov.uk/namespaces/legislation',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        # 1. استخراج العنوان الرئيسي للقانون من Metadata
        main_title = response.xpath("//dc:title/text()", namespaces=ns).get()
        if not main_title:
            main_title = response.xpath("//*[local-name()='Title']/text()").get() or "UK Law"
        
        # 2. البحث عن المواد (Sections) داخل Body القانون فقط لتجنب الملاحق
        articles = response.xpath("//ukl:Body//ukl:P1group", namespaces=ns)
        if not articles:
            articles = response.xpath("//*[local-name()='Body']//*[local-name()='P1group']")
        
        self.logger.info(f"Found {len(articles)} primary sections in XML Body.")

        for i, art in enumerate(articles):
            # استخراج اسم الباب (Part) الذي تتبعه هذه المادة
            part_title = art.xpath("ancestor::ukl:Part/ukl:Title/text()", namespaces=ns).get()
            if not part_title:
                part_title = art.xpath("ancestor::*[local-name()='Part']/*[local-name()='Title']/text()").get()
            current_part = part_title.strip() if part_title else "General Provisions"

            # استخراج عنوان المادة (Title)
            section_title = art.xpath("./ukl:Title/text()", namespaces=ns).get()
            if not section_title:
                section_title = art.xpath(".//ukl:Title/text()", namespaces=ns).get()
            final_title = section_title.strip() if section_title else "Untitled Section"
            
            # استخراج رقم المادة (Pnumber)
            section_number = art.xpath("./ukl:P1/ukl:Pnumber/text()", namespaces=ns).get()
            if not section_number:
                section_number = art.xpath(".//ukl:Pnumber/text()", namespaces=ns).get()
            final_number = section_number.strip() if section_number else f"N/A"

            # استخراج النص (جمع كل نصوص الفقرات)
            body_parts = art.xpath(".//ukl:Text//text()", namespaces=ns).getall()
            if not body_parts:
                body_parts = art.xpath(".//*[local-name()='Text']//text()").getall()
            article_body = " ".join([t.strip() for t in body_parts if t.strip()])

            # دمج المعلومات في العنوان
            full_title = f"{main_title.strip()} - {current_part} - {final_title}"

            yield LawItem(
                title=full_title,
                original_text=article_body if article_body else "Error When Extracting",
                country=self.country,
                category=self.section,
                article_number=final_number,
                source_url=response.url,
                date_scraped="now"
            )
