from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_laws():
    return {"laws": []}

@router.get("/{law_id}")
async def get_law(law_id: int):
    return {"law_id": law_id}
