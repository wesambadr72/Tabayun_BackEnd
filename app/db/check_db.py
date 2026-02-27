from sqlalchemy import inspect
from app.db.database import engine

def check_tables():
    print(f"Checking connection to: {engine.url.database}")
    print(f"Host: {engine.url.host}")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print("\n✅ Tables found in database:")
        for table in tables:
            print(f" - {table}")
    else:
        print("\n❌ No tables found! Check if you are looking at the right database.")

if __name__ == "__main__":
    check_tables()