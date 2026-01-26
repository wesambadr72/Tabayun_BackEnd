from fastapi import APIRouter

router = APIRouter()

@router.post("/query")
async def chat_query(query: str):
    return {"response": "AI Response", "source": "Legal Reference"}
