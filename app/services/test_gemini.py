import google.generativeai as genai

genai.configure(api_key="AIzaSyCfKoT5aYj66CSF7gUqYsZo1nd_u8Li4LE")

model = genai.GenerativeModel("models/gemini-1.5-flash")

response = model.generate_content("Cây bạc hà có tác dụng gì?")
print(response.text)
