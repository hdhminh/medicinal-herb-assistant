# 🌿 Hệ thống Hỏi Đáp Dược Liệu — Summer 2025

Một ứng dụng Web sử dụng **FastAPI + React** tích hợp mô hình **Gemini** để hỗ trợ người dùng tìm hiểu và đặt câu hỏi về các cây thuốc dân gian Việt Nam.

> Tác giả: **Nguyễn Hà Khuê**  
> 📧 Email: [marijuana.work@gmail.com](mailto:marijuana.work@gmail.com)

---

## 🏗 Cấu trúc thư mục

```
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── data/
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
└── README.md
```

---

## 🚀 Hướng dẫn cài đặt

### 1. Clone về máy

```bash
git clone <url-repo>
cd project-root
```

---

## 🖥 Backend (FastAPI + Gemini)

### 🔧 Cài đặt môi trường (Python >= 3.10)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# hoặc: source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### 📁 Tạo file `.env` trong `backend/`

```dotenv
GOOGLE_API_KEY=your_gemini_api_key_here
```

> 🔑 Dùng key từ Google AI Studio (Gemini 1.5 Flash hoặc Pro)

### ▶️ Chạy server

```bash
uvicorn app.main:app --reload
```

Mở trình duyệt: http://localhost:8000/docs để kiểm thử API.

---

## 💻 Frontend (React)

### 🧱 Cài đặt dependencies

```bash
cd frontend
npm install
```

> Đảm bảo đã cài `Node.js` v16+ và `npm`

### ▶️ Chạy frontend

```bash
npm start
```

Truy cập: http://localhost:3000

---

## 🎯 Tính năng

- Giao diện đơn giản, hiện đại và dễ sử dụng
- Chọn cây thuốc theo mã / tên từ dropdown
- Đặt câu hỏi tự nhiên bằng tiếng Việt
- Nhận câu trả lời từ mô hình AI (Gemini)
- Trích dẫn nguồn tham khảo chính xác
- Hiển thị kết quả dưới dạng markdown

---

## 📷 Screenshot

![UI screenshot](https://i.ibb.co/bgqPCWGV/UI-screenshot.png) <!-- nếu có -->

---

## 📌 Ghi chú

- Dữ liệu cây thuốc nằm ở file `backend/app/data/herbs_sample.json`
- Hệ thống hỗ trợ thêm cây thuốc mới dễ dàng bằng JSON
- Nếu bạn thấy dự án hữu ích, hãy ⭐ nó nhé!

---

## 📫 Liên hệ

- Nguyễn Hà Khuê  
- Email: [marijuana.work@gmail.com](mailto:marijuana.work@gmail.com)