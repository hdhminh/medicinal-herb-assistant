from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.services.herb_service import get_herb_info
from app.services.googleai_service import generate_answer_gemini
from app.services.link_preview import get_title_from_url
import os
import shutil
import json

router = APIRouter()

HERB_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "herbs_sample.json")

class HerbQuery(BaseModel):
    code: str
    question: str

@router.post("/ask")
async def ask_herb(query: HerbQuery):
    herb = get_herb_info(query.code)
    if not herb:
        return {"answer": "Không tìm thấy thông tin về mã cây đã nhập.", "source": None}
    answer_text = generate_answer_gemini(herb, query.question)
    source_url = herb.get("source")
    source_title = await get_title_from_url(source_url) if source_url else None
    return {
        "answer": answer_text,
        "source": source_url,
        "source_title": source_title
    }

@router.post("/identify")
async def identify_herb(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Vui lòng gửi một tệp hình ảnh.")
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        herb_code = "0001_bac_ha"  # Replace with actual classification
        herb = get_herb_info(herb_code)
        if not herb:
            raise HTTPException(status_code=404, detail="Không tìm thấy thông tin về cây thuốc.")
        question = "Xác định cây thuốc trong hình và mô tả công dụng của nó."
        answer_text = generate_answer_gemini(herb, question)
        source_url = herb.get("source")
        source_title = await get_title_from_url(source_url) if source_url else None
        return {
            "answer": answer_text,
            "source": source_url,
            "source_title": source_title
        }
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@router.get("/list")
async def list_herbs():
    try:
        with open(HERB_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tải danh sách cây thuốc: {str(e)}")