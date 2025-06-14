from fastapi import APIRouter, HTTPException
from app.models.herb_model import HerbQuery, HerbAnswer
from app.services.herb_service import get_herb_info
# from app.services.openai_service import generate_answer
from app.services.googleai_service import generate_answer_gemini
from app.services.link_preview import get_title_from_url

router = APIRouter()
 
@router.post("/ask", response_model=HerbAnswer)
async def ask_herb(query: HerbQuery):
    herb = get_herb_info(query.code)
    if not herb:
        return {"answer": "Không tìm thấy thông tin về mã cây đã nhập.", "source": None}

    answer_text = generate_answer_gemini(herb, query.question)
    # Lấy source và title
    source_url = herb.get("source")
    source_title = await get_title_from_url(source_url) if source_url else None

    return HerbAnswer(
        answer=answer_text,
        source=source_url,
        source_title=source_title
    )
