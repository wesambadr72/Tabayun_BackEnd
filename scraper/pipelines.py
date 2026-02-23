from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import LegalContent, Category
from scraper.items import LawItem

class DatabasePipeline:
    """
    خط معالجة لحفظ القوانين المستخرجة في قاعدة البيانات.
    """
    def open_spider(self, spider):
        self.db = SessionLocal()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        if not isinstance(item, LawItem):
            return item
            
        try:
            # 1. البحث عن أو إنشاء القسم (Category)
            category_name = item.get("category")
            category = self.db.query(Category).filter(Category.name == category_name).first()
            if not category:
                category = Category(name=category_name)
                self.db.add(category)
                self.db.commit()
                self.db.refresh(category)
            
            # 2. البحث عن القانون لتجنب التكرار (بناءً على الرابط ورقم المادة)
            existing_law = self.db.query(LegalContent).filter(
                LegalContent.source_url == item.get("source_url"),
                LegalContent.article_number == item.get("article_number")
            ).first()
            
            if existing_law:
                spider.logger.info(f"Updating existing law: {item.get('title')}")
                existing_law.title = item.get("title")
                existing_law.original_text = item.get("original_text")
                # existing_law.updated_at is handled by DB onupdate=func.now() usually, 
                # but we can set it if we want to force update timestamp
            else:
                spider.logger.info(f"Saving new law: {item.get('title')}")
                new_law = LegalContent(
                    title=item.get("title"),
                    country=item.get("country"),
                    category_id=category.id,
                    article_number_text = item.get("article_number", ""),    
                    original_text=item.get("original_text"),
                    simplified_text="", # سيتم ملؤه لاحقاً بواسطة AI Simplifier
                    source_url=item.get("source_url"),
                    is_live=1
                )
                self.db.add(new_law)
                
            self.db.commit()
            
        except Exception as e:
            spider.logger.error(f"Error saving item to database: {e}")
            self.db.rollback()
            
        return item
