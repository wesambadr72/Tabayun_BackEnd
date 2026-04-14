from sqlalchemy import text
from app.db.database import engine

def create_priority_laws_view():
    """
    أنشأ View ذكي يجمع أهم 10 مواد سعودية لكل قسم، 
    ويجلب آلياً "أكثر مادة مشابهة" لها من بريطانيا وألمانيا باستخدام الـ Embedding.
    """
    # نقوم بحذف الـ View القديم أولاً لتجنب تعارض أسماء الأعمدة
    drop_sql = "DROP VIEW IF EXISTS priority_legal_contents;"
    
    view_sql = """
    CREATE VIEW priority_legal_contents AS
    WITH SaudiTopTen AS (
        -- 1. اختيار أهم 10 مواد سعودية لكل قسم
        SELECT *,
               id as saudi_reference_id, -- المادة السعودية هي المرجع لنفسها
               ROW_NUMBER() OVER (
                   PARTITION BY category_id 
                   ORDER BY importance_score DESC, id ASC
               ) as rank_in_category
        FROM legal_contents
        WHERE country = 'sa' AND importance_score >= 8
    ),
    MatchedLaws AS (
        -- 2. البحث عن أكثر مادة مشابهة من الدول الأخرى
        SELECT DISTINCT ON (saudi_priority.id, other_country_law.country)
               other_country_law.*,
               saudi_priority.id as saudi_reference_id, -- ربط المادة الأجنبية بمعرف المادة السعودية
               0 as rank_in_category
        FROM SaudiTopTen AS saudi_priority
        CROSS JOIN LATERAL (
            SELECT *
            FROM legal_contents AS other_country_law
            WHERE other_country_law.country != 'sa' 
              AND other_country_law.category_id = saudi_priority.category_id
              AND other_country_law.embedding IS NOT NULL
            ORDER BY other_country_law.embedding <=> saudi_priority.embedding
            LIMIT 1
        ) AS other_country_law
        WHERE saudi_priority.rank_in_category <= 10
    )
    -- 3. الدمج مع ترتيب يضع المادة السعودية متبوعة بتوائمها العالمية
    SELECT * FROM SaudiTopTen WHERE rank_in_category <= 10
    UNION ALL
    SELECT * FROM MatchedLaws
    ORDER BY saudi_reference_id, country DESC; -- ترتيب يجمع "العائلة" الواحدة معاً
    """
    
    with engine.connect() as connection:
        # حذف الـ View القديم
        connection.execute(text(drop_sql))
        # إنشاء الـ View الجديد
        connection.execute(text(view_sql))
        connection.commit()
        print("✅ Database View 'priority_legal_contents' recreated successfully with Vector Matching.")

if __name__ == "__main__":
    create_priority_laws_view()