import os
import json
import torch
from torchvision import transforms
from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from PIL import Image
import io

from app.services.herb_service import get_herb_info
from app.services.googleai_service import generate_answer_gemini
from app.services.link_preview import get_title_from_url
from CV_training.models.dinov2_classifier import create_dinov2_classifier

router = APIRouter()

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
async def identify_herb(file: UploadFile = File(...)):
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
        question = "Xác định cây thuốc trong hình và mô tả công dụng của nó."
        answer_text = generate_answer_gemini(herb, question, "tóm tắt")
        source_url = herb.get("source")
        source_title = await get_title_from_url(source_url) if source_url else None

        return {
            "answer": answer_text,
            "herb_code": herb_code,
            "confidence": confidence,
            "source": source_url,
            "source_title": source_title
        }
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