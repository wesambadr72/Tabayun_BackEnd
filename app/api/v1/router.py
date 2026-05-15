from fastapi import APIRouter
from app.api import auth, laws, admin, chat, comparison, search

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(laws.router, prefix="/laws", tags=["laws"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(comparison.router, prefix="/comparison", tags=["comparison"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
