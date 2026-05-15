from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# إضافة خيارات الاتصال لدعم pgvector
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    from app.db import models  # استيراد الموديلات هنا لضمان تسجيلها في Base.metadata
    print(f"Connecting to database: {engine.url.database}")
    print(f"Tables to be created: ")
    for key in Base.metadata.tables.keys():
        print(f" - {key}")

    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def reset_db():
    from app.db import models
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset successfully!")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    # reset_db()
