from fastapi import APIRouter

router = APIRouter()

@router.get("/compare")
async def compare_laws(country_a: str, country_b: str):
    return {"comparison": f"Comparing laws between {country_a} and {country_b}"}
