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
        # هذا مثال بسيط، وسيحتاج لتخصيص لكل موقع لاحقاً
        
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
        # استخراج العنوان الرئيسي
        main_title = response.css("h1::text").get() or response.css("title::text").get()
        if not main_title:
            main_title = f"Law from {self.country} - {self.section}"
            
        # استخراج النص الكامل باستخدام XPath لضمان عدم تفويت أي جزء (خاصة النصوص التي لم تلتقطها المحددات السابقة)
        # نستبعد العناصر غير الضرورية مثل القوائم والترويسة
        content_list = response.xpath('//body//*[not(self::script) and not(self::style) and not(ancestor::nav) and not(ancestor::header) and not(ancestor::footer)]/text()').getall()
        full_content = "\n".join([t.strip() for t in content_list if t.strip()])
            
        # تنظيف النص
        full_content = full_content.strip()
        
        # نمط Regex محسن لالتقاط "المادة" ورقمها
        # التحديث: يشمل الأرقام (0-9، ٠-٩) والأقواس () لضمان عدم تفويت "المادة 5" أو "المادة (5)"
        article_pattern = re.compile(r'(?:^|\n)(المادة\s+(?:[\u0600-\u06FF0-9٠-٩\(\)]+\s*){1,5})', re.MULTILINE)
        
        matches = list(article_pattern.finditer(full_content))
        
        if matches:
            # معالجة المقدمة (ما قبل المادة الأولى)
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
                current_article_title = match.group(1).strip().replace('\n', ' ') # تنظيف العنوان من النزول للسطر
                start_pos = match.end()
                
                # نهاية النص هي بداية المادة التالية، أو نهاية الملف للمادة الأخيرة
                end_pos = matches[i+1].start() if i + 1 < len(matches) else len(full_content)
                
                article_body = full_content[start_pos:end_pos].strip()
                
                # دمج العنوان مع النص في original_text ليكون كاملاً
                full_article_text = f"{current_article_title}\n{article_body}"
                
                # إنشاء معرف فريد للرابط
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
