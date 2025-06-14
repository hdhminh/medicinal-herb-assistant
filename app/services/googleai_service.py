import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("models/gemini-1.5-flash")

def generate_answer_gemini(herb: dict, question: str) -> str:
    content = f"""
        Bạn là một chuyên gia thảo dược. Dưới đây là thông tin chi tiết về cây thuốc:

        Tên: {herb.get('name')}
        Tên khoa học: {herb.get('scientific_name')}
        Mô tả: {herb.get('description')}
        Công dụng: {herb.get('uses')}
        Cách dùng: {herb.get('usage')}
        Lưu ý: {herb.get('precautions')}
        Nguồn: {herb.get('source')}

        Dựa vào thông tin trên, hãy trả lời câu hỏi sau đầy đủ, chính xác và không thêm suy luận chủ quan:

        Câu hỏi: {question}
        """


    try:
        response = model.generate_content(content)
        return response.text.strip()
    except Exception as e:
        return f"[Lỗi Gemini] {e}"
