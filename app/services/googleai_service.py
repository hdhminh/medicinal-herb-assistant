import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("models/gemini-1.5-flash")

def generate_answer_gemini(herb: dict, question: str, answer_type: str = "tóm tắt") -> str:
    prompt_instruction = {
        "tóm tắt": "Hãy trả lời câu hỏi sau một cách ngắn gọn, súc tích và đi thẳng vào vấn đề:",
        "đầy đủ": "Hãy trả lời câu hỏi sau một cách đầy đủ thông tin:",
        "chi tiết": "Hãy trả lời câu hỏi sau một cách chi tiết, giải thích cặn kẽ và cung cấp thêm các ví dụ nếu có:"
    }
    
    instruction = prompt_instruction.get(answer_type, prompt_instruction["tóm tắt"])

    content = f"""
        Bạn là một chuyên gia thảo dược. Dưới đây là thông tin chi tiết về cây thuốc:

        Tên: {herb.get('name')}
        Tên khoa học: {herb.get('scientific_name')}
        Mô tả: {herb.get('description')}
        Công dụng: {herb.get('uses')}
        Cách dùng: {herb.get('usage')}
        Lưu ý: {herb.get('precautions')}
        Nguồn: {herb.get('source')}

        Dựa vào thông tin trên, {instruction}

        **Quan trọng**: Hãy định dạng câu trả lời bằng Markdown để dễ đọc. Sử dụng tiêu đề, in đậm, in nghiêng và danh sách khi cần thiết.

        Câu hỏi: {question}
        """


    try:
        response = model.generate_content(content)
        return response.text.strip()
    except Exception as e:
        return f"[Lỗi Gemini] {e}"
