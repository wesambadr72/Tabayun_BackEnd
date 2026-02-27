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

        for source in sources:
            yield scrapy.Request(
                url=source["base_url"],
                callback=self.parse,
                meta={"source_info": source}
            )

    def parse(self, response):
        source_info = response.meta["source_info"]
        self.logger.info(f"Scraping {source_info['name']} ({source_info['base_url']})")
        
        # منطق استخراج البيانات (يعتمد على نوع الموقع)
        
        # افتراض: إذا كان الرابط مباشراً لقانون (LawDetails أو PDF)
        if "LawDetails" in response.url or response.url.endswith(".pdf"):
            yield from self.parse_law_detail(response)
        else:
            # إذا كان فهرس (Index)، نحاول استخراج الروابط
            # مثال لـ WorldLII أو غيره
            links = response.css("a::attr(href)").getall()
            for link in links:
                if "law" in link.lower() or "act" in link.lower():
                     yield response.follow(link, callback=self.parse_law_detail, meta=response.meta)
            
            # If it's a direct page (like sa_boe_traffic_law), treat it as law detail directly
            if "LawDetails" in source_info.get("base_url", ""):
                 yield from self.parse_law_detail(response)


    def parse_law_detail(self, response):
        source_info = response.meta.get("source_info", {})
        main_title = response.css("h1::text").get() or response.css("title::text").get()
        if not main_title:
            main_title = f"Law from {self.country} - {self.section}"

        # ---------------------------------------------------------
        # الطريقة الأولى: الاستخراج المباشر عبر الهيكل (Selectors) - الأدق
        # ---------------------------------------------------------
        # نبحث عن الحاويات التي تمثل المواد بناءً على تحليل المستخدم
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
            return # انتهينا، لا داعي لإكمال الكود للطريقة القديمة

        # ---------------------------------------------------------
        # الطريقة الثانية (الاحتياطية): الاستخراج الشامل + Regex
        # تستخدم فقط إذا لم نجد الهيكل div.article_item
        # ---------------------------------------------------------
        self.logger.warning("Structured articles not found, falling back to full-text regex parsing.")
        
        # استخراج النص الكامل باستخدام XPath لضمان عدم تفويت أي جزء
        content_list = response.xpath('//body//*[not(self::script) and not(self::style) and not(ancestor::nav) and not(ancestor::header) and not(ancestor::footer)]/text()').getall()
        full_content = "\n".join([t.strip() for t in content_list if t.strip()])
            
        # تنظيف النص
        full_content = full_content.strip()
        
        # نمط Regex محسن لالتقاط "المادة" ورقمها
        article_pattern = re.compile(r'(?:^|\n)(المادة\s+(?:[\u0600-\u06FF0-9٠-٩\(\)]+\s*){1,5})', re.MULTILINE)
        
        matches = list(article_pattern.finditer(full_content))
        
        if matches:
            # ... (نفس كود الـ Regex السابق لمعالجة المقدمة والمواد)
            preamble_end = matches[0].start()
            preamble = full_content[:preamble_end].strip()
            
            if preamble:
                yield LawItem(
                    title=f"{main_title.strip()} - المقدمة",
                    original_text=preamble,
                    country=self.country,
                    category=self.section,
                    article_number="0",
                    source_url=f"{response.url}#preamble",
                    date_scraped="now"
                )
            
            # معالجة المواد
            for i, match in enumerate(matches):
                current_article_title = match.group(1).strip().replace('\n', ' ')
                start_pos = match.end()
                end_pos = matches[i+1].start() if i + 1 < len(matches) else len(full_content)
                article_body = full_content[start_pos:end_pos].strip()
                
                safe_article_num = current_article_title.replace(" ", "_")
                
                yield LawItem(
                    title=f"{main_title.strip()} - {current_article_title}",
                    original_text=article_body if article_body else current_article_title,
                    country=self.country,
                    category=self.section,
                    article_number=current_article_title, 
                    source_url=f"{response.url}#{safe_article_num}", 
                    date_scraped="now"
                )
        else:
            # لم يتم العثور على تقسيم "المادة"
            yield LawItem(
                title=main_title.strip(),
                original_text=full_content[:50000],
                country=self.country,
                category=self.section,
                article_number=source_info.get("article_number", "Full Text"),
                source_url=response.url,
                date_scraped="now"
            )
