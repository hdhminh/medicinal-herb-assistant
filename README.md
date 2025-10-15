# 🌿 Hệ thống Hỏi Đáp Dược Liệu

Một hệ thống trí tuệ nhân tạo toàn diện cho việc nhận diện và tư vấn về các loại dược liệu dân gian Việt Nam, tích hợp công nghệ học máy tiên tiến và giao diện người dùng thân thiện.

> **Tác giả**: Nguyễn Hà Khuê, Huỳnh Đoàn Hoàng Minh, Lê Hạc Du


---

## 📋 Mục lục

- [Tổng quan](#-tổng-quan)
- [Tính năng chính](#-tính-năng-chính)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Cài đặt và chạy](#-cài-đặt-và-chạy)
- [API Documentation](#-api-documentation)
- [Mô hình Computer Vision](#-mô-đun-computer-vision)
- [Cơ sở dữ liệu](#-cơ-sở-dữ-liệu)
- [Giao diện người dùng](#-giao-diện-người-dùng)
- [Đóng góp](#-đóng-góp)
- [Giấy phép](#-giấy-phép)

---

## 🎯 Tổng quan

Hệ thống Hỏi Đáp Dược Liệu là một ứng dụng web thông minh kết hợp trí tuệ nhân tạo và thị giác máy tính để:

- **Trả lời câu hỏi** về các loại dược liệu Việt Nam bằng ngôn ngữ tự nhiên
- **Nhận diện hình ảnh** các loại thảo dược từ ảnh tải lên
- **Cung cấp thông tin chi tiết** về công dụng, cách dùng và lưu ý an toàn
- **Trích dẫn nguồn gốc** đáng tin cậy cho mọi thông tin

Dự án được phát triển trong khuôn khổ, tập trung vào việc ứng dụng công nghệ AI hiện đại vào lĩnh vực y học cổ truyền Việt Nam.

---

## ✨ Tính năng chính

### 🤖 Hỏi đáp thông minh
- **Xử lý ngôn ngữ tự nhiên**: Hiểu và trả lời câu hỏi bằng tiếng Việt
- **Mô hình AI tiên tiến**: Tích hợp Google Gemini 1.5 Flash
- **Đa cấp độ chi tiết**: Tóm tắt, đầy đủ, chi tiết
- **Trích dẫn nguồn**: Liên kết đến tài liệu y khoa uy tín

### 📷 Nhận diện hình ảnh
- **Công nghệ thị giác máy tính**: Mô hình DINOv2 state-of-the-art
- **Nhận diện chính xác**: Hơn 50 loại dược liệu phổ biến
- **Xử lý thời gian thực**: Kết quả nhanh chóng
- **Đánh giá độ tin cậy**: Hiển thị confidence score

### 💬 Phản hồi người dùng
- **Hệ thống feedback**: Thu thập ý kiến từ người dùng
- **Hỗ trợ đính kèm**: Upload hình ảnh minh họa

### 🎨 Giao diện hiện đại
- **Responsive Design**: Tương thích mọi thiết bị
- **UX tối ưu**: Dễ sử dụng, trực quan
- **Markdown rendering**: Hiển thị kết quả đẹp mắt
- **Dark/Light theme**: Chủ đề tùy chỉnh

---

## 🛠 Công nghệ sử dụng

### Backend
- **FastAPI**: Framework Python hiện đại, hiệu năng cao
- **Google Generative AI**: Mô hình Gemini cho xử lý ngôn ngữ
- **PyTorch**: Framework deep learning cho computer vision
- **Torchvision**: Thư viện xử lý ảnh
- **Uvicorn**: ASGI server cho FastAPI

### Frontend
- **React 19**: Library JavaScript hiện đại
- **Axios**: HTTP client cho API calls
- **React Router**: Điều hướng trang
- **React Icons**: Bộ icon phong phú
- **React Select**: Dropdown component
- **React Markdown**: Render markdown

### AI & ML
- **Google Gemini 1.5 Flash**: Mô hình ngôn ngữ lớn
- **DINOv2**: Vision transformer cho nhận diện ảnh
- **Torch Hub**: Model zoo của PyTorch

### Cơ sở dữ liệu
- **JSON**: Lưu trữ thông tin dược liệu
- **File system**: Quản lý hình ảnh và model

### Công cụ phát triển
- **Python 3.10+**: Ngôn ngữ backend
- **Node.js 16+**: Runtime frontend
- **Git**: Quản lý phiên bản
- **VS Code**: IDE chính

---

## 📁 Cấu trúc dự án

```
project-root/
├── app/                          # Backend FastAPI
│   ├── main.py                   # Entry point ứng dụng
│   ├── routers/
│   │   ├── herb_router.py        # API hỏi đáp & nhận diện
│   │   └── feedback_router.py    # API phản hồi
│   ├── services/
│   │   ├── herb_service.py       # Logic xử lý dược liệu
│   │   ├── googleai_service.py   # Tích hợp Gemini
│   │   └── link_preview.py       # Lấy tiêu đề URL
│   ├── data/
│   │   ├── herbs_sample.json     # Cơ sở dữ liệu dược liệu
│   │   └── images/               # Hình ảnh minh họa
│   └── models/                   # (Reserved for future)
├── frontend/                     # Frontend React
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUpload.jsx   # Component upload ảnh
│   │   │   ├── HerbsPage.jsx     # Hiển thị thông tin dược liệu
│   │   │   └── FeedbackPage.jsx  # Form phản hồi
│   │   ├── App.js                # Component chính
│   │   └── index.js              # Entry point
│   ├── public/                   # Static assets
│   └── package.json              # Dependencies
├── CV_training/                  # Pipeline training CV
│   ├── main.py                   # Script training chính
│   ├── config.py                 # Cấu hình training
│   ├── models/
│   │   ├── dinov2_classifier.py  # Model DINOv2
│   │   └── herb_cnn.py           # Custom CNN
│   ├── utils/                    # Utilities
│   ├── training/                 # Training logic
│   ├── data/                     # Data processing
│   └── README.md                 # Hướng dẫn CV
├── saved_models/                 # Model đã train
│   ├── herb_recognition_model.pth
│   └── model_metadata.json
├── uploads/                      # Ảnh upload từ user
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # File này
```

---

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống

- **Python**: 3.10 hoặc cao hơn
- **Node.js**: 16.0 hoặc cao hơn
- **CUDA**: 11.8+ (khuyến nghị cho GPU training)
- **RAM**: 8GB+ cho training, 4GB+ cho inference
- **Disk**: 10GB+ free space

### 1. Clone repository

```bash
git clone <repository-url>
cd project-root
```

### 2. Cài đặt Backend (FastAPI)

```bash
# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3. Cấu hình API Keys

Tạo file `.env` trong thư mục `app/`:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

> **Lưu ý**: Lấy API key từ [Google AI Studio](https://makersuite.google.com/app/apikey)

### 4. Cài đặt Frontend (React)

```bash
cd frontend
npm install
```

### 5. Chạy hệ thống

```bash
# Terminal 1: Backend
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm start
```

### 6. Truy cập ứng dụng

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/

---

## 📚 API Documentation

### Endpoints chính

#### `/herb/ask` - Hỏi đáp về dược liệu
```http
POST /herb/ask
Content-Type: application/json

{
  "code": "0001_bac_ha",
  "question": "Bạc hà dùng để chữa bệnh gì?",
  "answer_type": "đầy đủ"
}
```

**Response**:
```json
{
  "answer": "Bạc hà được sử dụng để...",
  "source": "https://example.com",
  "source_title": "Thông tin về bạc hà",
  "name": "Bạc hà",
  "scientific_name": "Mentha arvensis L.",
  "description": "...",
  "uses": "...",
  "usage": "...",
  "precautions": "..."
}
```

#### `/herb/identify` - Nhận diện từ hình ảnh
```http
POST /herb/identify
Content-Type: multipart/form-data

file: <image_file>
detail_level: "tóm tắt"
```

#### `/herb/list` - Danh sách dược liệu
```http
GET /herb/list
```

#### `/herb/{code}/images` - Lấy hình ảnh
```http
GET /herb/{code}/images?limit=5&offset=0
```

#### `/feedback` - Gửi phản hồi
```http
POST /feedback
Content-Type: multipart/form-data

feedback_type: "bug_report"
comments: "Tôi gặp lỗi..."
user_email: "user@example.com"
image: <optional_file>
```

---

## 🧠 Mô-đun Computer Vision

### Mô hình DINOv2

Dự án sử dụng kiến trúc **DINOv2** (Distilled Vision Transformer) - một trong những mô hình thị giác máy tính tiên tiến nhất hiện nay.

#### Cấu hình model
- **Architecture**: DINOv2 ViT-L/14 (307M parameters)
- **Input size**: 224x224 pixels
- **Classes**: 50+ loại dược liệu Việt Nam
- **Accuracy**: >95% trên tập test

#### Training pipeline

```bash
cd CV_training
python main.py --model dinov2_vitl14 --epochs 50 --batch-size 16
```

#### Các model có sẵn
- `dinov2_vits14`: Nhỏ gọn, nhanh (22M params)
- `dinov2_vitb14`: Cân bằng (87M params)
- `dinov2_vitl14`: Độ chính xác cao (307M params)
- `dinov2_vitg14`: Tối ưu nhất (1.1B params)
- `custom_cnn`: CNN tùy chỉnh (2M params)

---

## 🗄 Cơ sở dữ liệu

### Cấu trúc dữ liệu dược liệu

File `app/data/herbs_sample.json` chứa thông tin về 50+ loại dược liệu:

```json
{
  "id": 1,
  "code": "0001_bac_ha",
  "name": "Bạc hà",
  "scientific_name": "Mentha arvensis L.",
  "description": "Mô tả chi tiết về cây...",
  "uses": "Công dụng chính...",
  "usage": "Cách sử dụng...",
  "precautions": "Lưu ý an toàn...",
  "source": "https://nhathuoclongchau.com.vn/..."
}
```

### Thêm dược liệu mới

1. Thêm entry vào `herbs_sample.json`
2. Tạo thư mục `app/data/images/{code}/`
3. Đặt hình ảnh minh họa vào thư mục

---

## 🎨 Giao diện người dùng

### Trang chính
- **Upload ảnh**: Kéo thả hoặc chọn file
- **Chọn mức độ**: Tóm tắt/Đầy đủ/Chi tiết
- **Hiển thị kết quả**: Markdown formatting
- **Thông tin bổ sung**: Tên khoa học, nguồn gốc

### Responsive Design
- **Mobile-first**: Tối ưu cho điện thoại
- **Tablet**: Layout thích ứng
- **Desktop**: Giao diện đầy đủ tính năng

### UX Features
- **Loading states**: Hiển thị tiến trình
- **Error handling**: Thông báo lỗi rõ ràng
- **Image preview**: Xem trước ảnh upload
- **Copy to clipboard**: Sao chép kết quả

---

## 🔧 Phát triển nâng cao

### Training model CV

```bash
# Quick test
python CV_training/main.py --quick-test

# Custom dataset
python CV_training/main.py --data-path /path/to/dataset

# Advanced config
python CV_training/main.py --model dinov2_vitg14 --epochs 100 --lr 0.0001
```

### Thêm loại dược liệu mới

1. **Cập nhật database**:
   ```json
   {
     "id": 51,
     "code": "0051_ten_moi",
     "name": "Tên mới",
     // ... other fields
   }
   ```

2. **Thêm hình ảnh**: Tạo thư mục và upload ảnh

3. **Retrain model** (nếu cần):
   ```bash
   python CV_training/main.py
   ```

### Tùy chỉnh AI responses

Sửa file `app/services/googleai_service.py` để thay đổi prompt hoặc model.

---

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng:

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

### Hướng dẫn commit

```
feat: thêm tính năng mới
fix: sửa lỗi
docs: cập nhật tài liệu
style: chỉnh sửa format code
refactor: tái cấu trúc code
test: thêm/cập nhật tests
```

---

## 📄 Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.


## 📞 Liên hệ

**Nguyễn Hà Khuê**
- Email: [hakhueangie.work@gmail.com](mailto:hakhueangie.work@gmail.com)

**Huỳnh Đoàn Hoàng Minh**
- Email: [kuminhuynhdoan@gmail.com](mailto:kuminhuynhdoan@gmail.com)

**Lê Hạc Du**
- Email: [holyshot159@gmail.com](mailto:holyshot159@gmail.com)