import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { herbCodes } from "../constants/herbCodes";
import Select from "react-select";
import { FaRocket } from "react-icons/fa";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import HerbsPage from "./HerbsPage";
import FeedbackPage from "./FeedbackPage";

const HerbForm = () => {
  const [code, setCode] = useState("");
  const [question, setQuestion] = useState("");
  const [answerType, setAnswerType] = useState("tóm tắt");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  // 🔹 Camera + upload states
  const [selectedFile, setSelectedFile] = useState(null);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [error, setError] = useState("");

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // --- Camera setup ---
  useEffect(() => {
    let stream;
    if (isCameraOn) {
      navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((mediaStream) => {
          stream = mediaStream;
          if (videoRef.current) videoRef.current.srcObject = stream;
        })
        .catch((err) => {
          console.error("Camera error:", err);
          setError("Không thể mở camera.");
        });
    }
    return () => {
      if (stream) {
        stream.getTracks().forEach((t) => t.stop());
      }
    };
  }, [isCameraOn]);

  // --- Format response ---
  const formatResponse = (text) => {
    if (!text) return "";
    return text
      .replace(/### (.*?)\n/g, "<h3>$1</h3>")
      .replace(/## (.*?)\n/g, "<h2>$1</h2>")
      .replace(/# (.*?)\n/g, "<h1>$1</h1>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/\n/g, "<br />");
  };

  // --- Q&A ask ---
  const handleAsk = async () => {
    if (!code || !question) {
      setResponse({
        answer: "[Lỗi] Vui lòng chọn mã cây thuốc và nhập câu hỏi.",
        source: null,
      });
      return;
    }

    setLoading(true);
    setResponse(null);
    try {
      const res = await axios.post("http://localhost:8000/herb/ask", {
        code,
        question,
        answer_type: answerType,
      });
      setResponse(res.data);
    } catch (err) {
      setResponse({
        answer: "[Lỗi] Không thể lấy dữ liệu từ máy chủ.",
        source: null,
      });
    } finally {
      setLoading(false);
    }
  };

  // --- Upload handler ---
  const handleUpload = async (file) => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      setError("");
      const res = await fetch(
        "http://localhost:8000/herb/identify?detail_level=" +
          encodeURIComponent("tóm tắt"),
        { method: "POST", body: formData }
      );

      if (!res.ok) throw new Error("Upload failed");
      const result = await res.json();
      console.log("✅ Kết quả nhận diện:", result);
      setResponse({ answer: JSON.stringify(result, null, 2), source: null });
    } catch (err) {
      console.error(err);
      setError("Lỗi khi xử lý ảnh");
    }
  };

  // --- File upload ---
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      handleUpload(file);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  // --- NEW: context-aware send button ---
  const handleSendClick = () => {
    if (selectedFile) {
      // If we already have a captured/selected file, upload it
      handleUpload(selectedFile);
    } else {
      // Otherwise open the picker
      triggerFileInput();
    }
  };

  // --- Capture snapshot ---
  const handleCapture = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], "captured.jpg", { type: "image/jpeg" });
        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(blob));
        // keep existing behavior: auto-upload on capture
        handleUpload(file);
      }
    }, "image/jpeg");
  };

  return (
    <div style={styles.wrapper}>
      {/* Select herb + ask */}
      <Select
        options={herbCodes.map((item) => ({
          value: item.code,
          label: `${item.code} - ${item.name}`,
        }))}
        onChange={(selected) => setCode(selected?.value || "")}
        placeholder="🌿 Chọn mã cây thuốc..."
        styles={customSelectStyles}
      />

      <textarea
        placeholder="Gõ câu hỏi của bạn..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={4}
        style={styles.textarea}
      />

      <div style={styles.radioGroup}>
        {["tóm tắt", "đầy đủ", "chi tiết"].map((type) => (
          <label key={type} style={styles.radioLabel}>
            <input
              type="radio"
              value={type}
              checked={answerType === type}
              onChange={(e) => setAnswerType(e.target.value)}
              style={styles.radioInput}
            />
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </label>
        ))}
      </div>

      <button
        onClick={handleAsk}
        disabled={loading || !code || !question}
        style={styles.button}
      >
        {loading ? (
          <>
            <AiOutlineLoading3Quarters className="spin" style={{ marginRight: 6 }} />
            Đang gửi...
          </>
        ) : (
          <>
            <FaRocket style={{ marginRight: 6 }} />
            Gửi câu hỏi
          </>
        )}
      </button>

      {/* --- Upload / Camera Section --- */}
      <div style={{ marginTop: "40px" }}>
        <h2>📷 Nhận diện cây thuốc qua Ảnh / Camera</h2>

        {/* Hidden file input */}
        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleFileChange}
        />
        {/* Context-aware: if we already have a photo, send it; else open picker */}
        <button onClick={handleSendClick} style={styles.button}>
          Gửi ảnh
        </button>

        {/* Camera */}
        <button
          onClick={() => setIsCameraOn((prev) => !prev)}
          style={{ ...styles.button, marginTop: "10px" }}
        >
          {isCameraOn ? "Tắt camera" : "Bật camera"}
        </button>

        {isCameraOn && (
          <div>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              style={{ width: "300px", border: "1px solid black", marginTop: "10px" }}
            />
            <canvas ref={canvasRef} style={{ display: "none" }} />
            <button onClick={handleCapture} style={styles.button}>
              Chụp ảnh
            </button>
          </div>
        )}

        {/* Preview */}
        {previewUrl && (
          <div style={{ marginTop: "15px" }}>
            <strong>Ảnh đã chọn:</strong>
            <img
              src={previewUrl}
              alt="preview"
              style={{ width: "200px", marginTop: "10px", borderRadius: "8px" }}
            />
          </div>
        )}

        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>

      {/* --- Response --- */}
      {response && (
        <div style={styles.responseBox}>
          <strong style={styles.responseLabel}>Kết quả:</strong>
          {response.answer && (
            <p
              style={styles.responseText}
              dangerouslySetInnerHTML={{ __html: formatResponse(response.answer) }}
            />
          )}
          {response.source && (
            <>
              <strong style={styles.responseLabel}>Nguồn:</strong>
              <p style={styles.responseText}>
                <a href={response.source} target="_blank" rel="noopener noreferrer">
                  {response.source_title || response.source}
                </a>
              </p>
            </>
          )}
          <div style={styles.herbsPageBox}>
            <HerbsPage selectedCode={code} hasAnswer={true} />
          </div>

          <button
            style={{ ...styles.button, background: "linear-gradient(to right, #81c784, #66bb6a)" }}
            onClick={() => setShowFeedback(!showFeedback)}
          >
            {showFeedback ? "Ẩn Phản Hồi" : "Gửi Phản Hồi"}
          </button>
          {showFeedback && (
            <div style={styles.feedbackBox}>
              <FeedbackPage />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// --- Styles ---
const styles = {
  wrapper: {
    background: "var(--card-background)",
    padding: "30px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px var(--shadow-color)",
    animation: "fadeInUp 0.5s ease-in-out",
    maxWidth: "600px",
    margin: "40px auto",
  },
  textarea: {
    width: "100%",
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid var(--border-color)",
    fontSize: "16px",
    outline: "none",
    resize: "vertical",
    marginTop: "15px",
    fontFamily: "'Be Vietnam Pro', sans-serif",
  },
  button: {
    width: "100%",
    padding: "12px",
    borderRadius: "8px",
    background: "var(--primary-color)",
    color: "#fff",
    fontWeight: "bold",
    border: "none",
    cursor: "pointer",
    transition: "background 0.3s",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginTop: "15px",
    fontSize: "16px",
  },
  feedbackBox: { marginTop: "30px" },
  herbsPageBox: { marginTop: "30px" },
  responseBox: {
    marginTop: "30px",
    paddingTop: "20px",
    borderTop: "1px solid var(--border-color)",
  },
  responseLabel: {
    fontSize: "20px",
    fontWeight: "bold",
    color: "var(--primary-color)",
    marginBottom: "10px",
  },
  responseText: {
    lineHeight: "1.8",
    fontSize: "16px",
    marginBottom: "20px",
  },
  radioGroup: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "center",
    gap: "20px",
    margin: "20px 0",
  },
  radioLabel: { display: "flex", alignItems: "center", fontSize: "16px" },
  radioInput: { marginRight: "8px" },
};

const customSelectStyles = {
  control: (base) => ({
    ...base,
    borderRadius: "8px",
    padding: "4px",
    fontSize: "16px",
    borderColor: "var(--border-color)",
    boxShadow: "none",
    "&:hover": { borderColor: "var(--primary-color)" },
  }),
  menu: (base) => ({ ...base, borderRadius: "8px", zIndex: 100 }),
  option: (base, { isFocused }) => ({
    ...base,
    backgroundColor: isFocused ? "var(--background-color)" : "var(--card-background)",
    color: "var(--text-color)",
    fontSize: "16px",
  }),
};

export default HerbForm;
