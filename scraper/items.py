import scrapy

class LawItem(scrapy.Item):
    """
    نموذج البيانات المستخرجة من المواقع.
    يتم تمريره لاحقاً للـ Pipeline للحفظ في قاعدة البيانات.
    """
    title = scrapy.Field()          
    original_text = scrapy.Field()  
    country = scrapy.Field()        
    category = scrapy.Field()
    article_number = scrapy.Field()       
    source_url = scrapy.Field()     
    date_scraped = scrapy.Field()   
