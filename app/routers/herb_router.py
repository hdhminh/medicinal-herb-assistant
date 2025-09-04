import os
import json
import torch
from torchvision import transforms
from fastapi import APIRouter, HTTPException, UploadFile, File, Request, Query
from fastapi.responses import FileResponse
from PIL import Image
import io
import shutil
from pydantic import BaseModel
from app.services.herb_service import get_herb_info
from app.services.googleai_service import generate_answer_gemini
from app.services.link_preview import get_title_from_url
from CV_training.models.dinov2_classifier import create_dinov2_classifier

router = APIRouter()

HERB_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "herbs_sample.json")

class HerbQuery(BaseModel):
    code: str
    question: str
    answer_type: str = "tóm tắt"

@router.post("/ask")
async def ask_herb(query: HerbQuery):
    herb = get_herb_info(query.code)
    if not herb:
        return {"answer": "Không tìm thấy thông tin về mã cây đã nhập.", "source": None}
    
    answer_text = generate_answer_gemini(herb, query.question, query.answer_type)
    source_url = herb.get("source")
    source_title = await get_title_from_url(source_url) if source_url else None

    response_data = {
        "answer": answer_text,
        "source": source_url,
        "source_title": source_title,
        "name": herb.get("name"),
        "scientific_name": herb.get("scientific_name"),
    }

    # Include description, uses, usage, precautions based on answer_type
    if query.answer_type == "đầy đủ" or query.answer_type == "chi tiết":
        response_data["description"] = herb.get("description")
        response_data["uses"] = herb.get("uses")
        response_data["usage"] = herb.get("usage")
        response_data["precautions"] = herb.get("precautions")
    
    if query.answer_type == "chi tiết":
        # Add more detailed info if available, for now it's the same as full
        pass

    return response_data

@router.get("/list")
async def list_herbs():
    try:
        with open(HERB_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tải danh sách cây thuốc: {str(e)}")

@router.get("/{herb_code}/images")
async def get_herb_images(herb_code: str, request: Request, limit: int = 5, offset: int = 0):
    image_dir = os.path.join(os.path.dirname(__file__), "..", "data", "images", herb_code)
    if not os.path.isdir(image_dir):
        raise HTTPException(status_code=404, detail="Không tìm thấy hình ảnh cho cây thuốc này.")
    
    try:
        image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
        image_files.sort()
        
        base_url = str(request.base_url)
        # Ensure base_url ends with a slash if it doesn't already
        if not base_url.endswith('/'):
            base_url += '/'
            
        image_urls = [f"{base_url}herb/images/{herb_code}/{f}" for f in image_files]
        
        return image_urls[offset:offset + limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đọc hình ảnh: {str(e)}")

# Transform cho ảnh
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Load checkpoint
model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "CV_training", "saved_models")
checkpoint_path = os.path.join(model_dir, "herb_recognition_model.pth")
metadata_path = os.path.join(model_dir, "model_metadata.json")

checkpoint = torch.load(checkpoint_path, map_location="cpu")

# Lấy số lớp
if "num_classes" in checkpoint:
    num_classes = checkpoint["num_classes"]
else:
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    num_classes = metadata["num_classes"]

# Lấy mapping idx -> label
if "class_names" in checkpoint:
    idx_to_label = {i: name for i, name in enumerate(checkpoint["class_names"])}
elif "class_to_idx" in checkpoint:
    idx_to_label = {v: k for k, v in checkpoint["class_to_idx"].items()}
else:
    raise KeyError("Checkpoint must contain 'class_names' or 'class_to_idx'")

# Tạo model DINOv2
cnn = create_dinov2_classifier(
    num_classes=num_classes,
    model_name="dinov2_vitl14",  # phải khớp với model khi train
    freeze_backbone=False
)

# Load state dict
if "model_state_dict" in checkpoint:
    cnn.load_state_dict(checkpoint["model_state_dict"])
else:
    cnn.load_state_dict(checkpoint)

cnn.eval()

@router.post("/identify")
async def identify_herb(file: UploadFile = File(...), detail_level: str = Query("tóm tắt")):
    print("✅ Nhận request /herb/identify")   

    contents = await file.read()
    if not contents:
        print("⚠️ Không có dữ liệu file upload")
        raise HTTPException(status_code=400, detail="Không có file tải lên.")

    try:
        from io import BytesIO
        image = Image.open(BytesIO(contents)).convert("RGB")
        print(f"📷 Đọc ảnh thành công: {file.filename}, size={image.size}, format={image.format}")
    except Exception as e:
        print(f"❌ Lỗi đọc ảnh: {e}")
        raise HTTPException(status_code=400, detail="File tải lên không phải hình ảnh hợp lệ.")

    input_tensor = transform(image).unsqueeze(0)  # [1,3,H,W]

    with torch.no_grad():
        outputs = cnn(input_tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        conf, pred = torch.max(probs, 1)
        herb_code = idx_to_label[pred.item()]
        confidence = conf.item()

    # Tìm thông tin trong herbs_sample.json
    herb = get_herb_info(herb_code)

    if herb:
        # Có thông tin metadata
        # The image has already been identified by the CV model.
        # The question for Gemini should reflect this, focusing on describing the identified herb.
        
        question_map = {
            "tóm tắt": f"Cây thuốc đã được xác định là {herb.get('name')} ({herb.get('scientific_name')}). Hãy tóm tắt công dụng, cách dùng và những lưu ý của nó.",
            "đầy đủ": f"Cây thuốc đã được xác định là {herb.get('name')} ({herb.get('scientific_name')}). Hãy cung cấp đầy đủ thông tin về công dụng, cách dùng và những lưu ý của nó.",
            "chi tiết": f"Cây thuốc đã được xác định là {herb.get('name')} ({herb.get('scientific_name')}). Hãy cung cấp thông tin chi tiết về công dụng, cách dùng và những lưu ý của nó, bao gồm mô tả."
        }
        question = question_map.get(detail_level, question_map["tóm tắt"])

        answer_text = generate_answer_gemini(herb, question, detail_level)
        source_url = herb.get("source")
        source_title = await get_title_from_url(source_url) if source_url else None

        # Include description, uses, usage, precautions based on detail_level
        response_data = {
            "answer": answer_text,
            "herb_code": herb_code,
            "confidence": confidence,
            "source": source_url,
            "source_title": source_title,
            "name": herb.get("name"),
            "scientific_name": herb.get("scientific_name"),
        }

        if detail_level == "đầy đủ" or detail_level == "chi tiết":
            response_data["description"] = herb.get("description")
            response_data["uses"] = herb.get("uses")
            response_data["usage"] = herb.get("usage")
            response_data["precautions"] = herb.get("precautions")
        
        if detail_level == "chi tiết":
            # Add more detailed info if available, for now it's the same as full
            pass

        return response_data
    else:
        # Không có metadata → trả về thẳng kết quả model
        print(f"⚠️ Không tìm thấy thông tin trong herbs_sample.json cho {herb_code}")
        return {
            "answer": f"Mô hình dự đoán đây là cây: {herb_code}. Nhưng chưa có thêm thông tin chi tiết trong cơ sở dữ liệu.",
            "herb_code": herb_code,
            "confidence": confidence,
            "source": None,
            "source_title": None
        }
