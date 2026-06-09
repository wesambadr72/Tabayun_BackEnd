from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.chat import ChatMessage, SimpleChatResponse
from app.services.ai_processor.rag_chatbot import RAGChatbot
from app.utils.helpers import get_language_code, get_target_language_code

router = APIRouter()


@router.post("/query", response_model=SimpleChatResponse)
async def chat_query(
    chat_in: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Answer a legal chat question using the RAG chatbot."""
    try:
        chatbot = RAGChatbot(db)
        full_lang = get_target_language_code(lang=chat_in.language, user_lang=current_user.language)
        lang_code = get_language_code(full_lang)

        result = await chatbot.ask(
            question=chat_in.message,
            country_filter=None,
            language=lang_code,
            user_name=current_user.full_name,
            user_country=current_user.country,
        )

        if "error" in result:
            logger.error("Chatbot returned error: {}", result["error"])
            raise HTTPException(status_code=502, detail="AI assistant failed to generate an answer")

        return {
            "response": result.get("answer", "Sorry, I couldn't find a direct answer right now."),
            "source": result.get("source_article"),
            "sources": result.get("sources", []),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled chat query error")
        raise HTTPException(
            status_code=502,
            detail=f"Chat service error: {exc.__class__.__name__}",
        )
