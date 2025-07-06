from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class FeedbackRequest(BaseModel):
    feedback_type: str
    comments: str
    user_email: str | None = None
    other_details: str | None = None

@router.post("/feedback")
async def submit_feedback(
    feedback_type: str = Form(...),
    comments: str = Form(...),
    user_email: str = Form(None),
    other_details: str = Form(None),
    image: UploadFile = File(None)
):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("GMAIL_ADDRESS")
        sender_password = os.getenv("GMAIL_APP_PASSWORD")
        receiver_email = "your.feedback.receiver@gmail.com"  # Replace with your email

        if not sender_email or not sender_password:
            raise HTTPException(status_code=500, detail="Email configuration missing in .env")

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = f"Phản Hồi: {feedback_type}"

        body = f"""
        Loại Phản Hồi: {feedback_type}
        Nội Dung: {comments}
        Chi Tiết Khác: {other_details or 'Không cung cấp'}
        Email Người Gửi: {user_email or 'Không cung cấp'}
        """
        msg.attach(MIMEText(body, "plain"))

        if image:
            if not image.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Tệp đính kèm phải là hình ảnh.")
            image_data = await image.read()
            image_mime = MIMEImage(image_data, name=image.filename)
            msg.attach(image_mime)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return {"message": "Phản hồi đã được gửi thành công qua email."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gửi email: {str(e)}")