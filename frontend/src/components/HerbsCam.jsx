import React, { useRef, useState, useEffect } from "react";

export default function HerbCam() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [stream, setStream] = useState(null);
  const [herbResult, setHerbResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Attach stream to video when available
  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  const startCamera = async () => {
    try {
      const userStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(userStream); // store stream
      setIsCameraOn(true);
      setError("");
    } catch (err) {
      console.error("Camera error:", err);
      setError("Không thể mở camera. Hãy kiểm tra quyền truy cập.");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsCameraOn(false);
    setHerbResult(null);
  };

  return (
    <div style={styles.container}>
      {!isCameraOn ? (
        <button onClick={startCamera} style={styles.button}>
          Mở cam
        </button>
      ) : (
        <>
          <p style={styles.camStatus}>🔴 Camera đang bật</p>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            style={styles.video}
          />
          <canvas ref={canvasRef} style={{ display: "none" }} />

          <div style={{ marginTop: "10px" }}>
            <button onClick={stopCamera} style={{ ...styles.button, background: "#d32f2f" }}>
              Tắt cam
            </button>
          </div>

          <div style={styles.resultBox}>
            {loading && <p style={styles.text}>Đang nhận diện...</p>}
            {error && <p style={styles.error}>{error}</p>}
            {herbResult && (
              <div>
                <h3 style={styles.caption}>{herbResult.name}</h3>
                <p><strong>Tên khoa học:</strong> {herbResult.scientific_name || "Không có dữ liệu"}</p>
                <p><strong>Mô tả:</strong> {herbResult.description || "Không có mô tả"}</p>
                <p><strong>Công dụng:</strong> {herbResult.uses || "Không có công dụng"}</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  container: {
    textAlign: "center",
    marginTop: "20px",
  },
  video: {
    width: "320px",
    height: "240px",
    borderRadius: "8px",
    border: "2px solid #4caf50",
    marginTop: "10px",
  },
  button: {
    padding: "10px 20px",
    margin: "5px",
    border: "none",
    borderRadius: "8px",
    background: "#4caf50",
    color: "white",
    fontSize: "16px",
    cursor: "pointer",
  },
  camStatus: {
    marginTop: "10px",
    color: "#d32f2f",
    fontWeight: "bold",
  },
  resultBox: {
    marginTop: "20px",
    padding: "10px",
    border: "1px solid #ccc",
    borderRadius: "8px",
  },
  text: { fontSize: "16px" },
  error: { color: "red" },
  caption: { fontWeight: "bold" },
};
