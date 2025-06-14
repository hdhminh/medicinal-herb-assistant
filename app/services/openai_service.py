import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(herb: dict, question: str) -> str:
    prompt = (
        f"Tên dược liệu: {herb['name']} ({herb['scientific_name']}).\n"
        f"Mô tả: {herb['description']}\n"
        f"Công dụng: {herb['uses']}\n"
        f"Cách dùng: {herb['usage']}\n"
        f"Lưu ý: {herb['precautions']}\n"
        f"Người dùng hỏi: {question}\n"
        f"Trả lời theo thông tin trên bằng tiếng Việt:"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": prompt }],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()
