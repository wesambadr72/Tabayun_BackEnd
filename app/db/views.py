from sqlalchemy import text
from app.db.database import engine

def create_priority_laws_view():
    """
    إنشاء View في قاعدة البيانات يختار أهم 25 مادة لكل دولة في كل قسم.
    نستخدم ROW_NUMBER() للترتيب واختيار الـ 25 الأولى.
    """
    view_sql = """
    CREATE OR REPLACE VIEW priority_legal_contents AS
    WITH RankedLaws AS (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY country, category_id 
                   ORDER BY importance_score DESC, id ASC
               ) as rank_in_category
        FROM legal_contents
    )
    SELECT *
    FROM RankedLaws
    WHERE rank_in_category <= 10;
    """
          #ناخذ أول و اهم 10 مواد لكل قسم و لكل دولة
    with engine.connect() as connection:
        connection.execute(text(view_sql))
        connection.commit()
        print("✅ Database View 'priority_legal_contents' created successfully.")

if __name__ == "__main__":
    create_priority_laws_view()