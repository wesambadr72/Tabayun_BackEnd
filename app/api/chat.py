from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.ai_processor.rag_chatbot import RAGChatbot
from app.schemas.chat import ChatMessage, SimpleChatResponse
from app.core.security import get_current_user
from app.db.models import User

router = APIRouter()

@router.post("/query", response_model=SimpleChatResponse)
async def chat_query(
    chat_in: ChatMessage, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    مسار المحادثة الذكية (RAG Chatbot):
    يستقبل سؤال المستخدم ويقوم بالبحث في القوانين ثم الإجابة باستخدام Gemini.
    """
    chatbot = RAGChatbot(db)
    
    # إلغاء فلتر الدولة للسماح للذكاء الاصطناعي بالوصول لكافة القوانين (السعودية والأجنبية) للإجابة بدقة
    country_filter = None
    
    # تحديد اللغة (افتراضياً العربية)
    language = "ar"
    
    result = await chatbot.ask(
        question=chat_in.message,
        country_filter=country_filter,
        language=language
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return {
        "response": result.get("answer", "Sorry, I couldn't find a direct answer right now."),
        "source": result.get("source_article", "Legal Reference Article")
    }
