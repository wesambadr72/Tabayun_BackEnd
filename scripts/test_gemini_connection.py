import asyncio
import sys
import os

# إضافة مسار المشروع الأساسي
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from google import genai

async def test_connection():
    # تنظيف اسم الموديل
    model_name = settings.GEMINI_MODEL_NAME.strip('"').strip("'")
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    print(f"📡 Testing with model: {model_name}")
    try:
        # تجربة إرسال طلب بسيط
        response = await client.aio.models.generate_content(
            model=model_name,
            contents="Say hello"
        )
        print("✅ Connection Successful!")
        print(f"🤖 Model Response: {response.text}")
    except Exception as e:
        print(f"❌ Connection Failed with '{model_name}': {e}")
        print("\n🔍 Listing ALL available models for your API Key:")
        try:
            # عرض كل الموديلات المتاحة بدون فلاتر معقدة
            models = client.models.list()
            for m in models:
                # طباعة الاسم فقط لنعرف الصيغة الصحيحة
                print(f" - {m.name}")
        except Exception as list_err:
            print(f"Could not list models: {list_err}")

if __name__ == "__main__":
    asyncio.run(test_connection())