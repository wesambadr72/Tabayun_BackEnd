from dataclasses import dataclass
from typing import Optional
import scrapy


@dataclass
class LegalItem(scrapy.Item):
    country = scrapy.Field()
    section = scrapy.Field()
    title = scrapy.Field()
    article_number = scrapy.Field()
    original_description = scrapy.Field()
    source_url = scrapy.Field()
    language = scrapy.Field()

