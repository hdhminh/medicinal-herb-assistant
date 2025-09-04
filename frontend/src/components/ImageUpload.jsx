import React, { useState, useRef } from 'react';
import axios from 'axios';
import { BiImageAdd } from 'react-icons/bi';
import HerbsPage from './HerbsPage'; // Import HerbsPage
import FeedbackPage from './FeedbackPage'; // Import FeedbackPage

const ImageUpload = () => {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [message, setMessage] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [detailLevel, setDetailLevel] = useState('tóm tắt'); // Default to 'Tóm tắt'
  const [showFeedback, setShowFeedback] = useState(false); // Add showFeedback state
  const fileInputRef = useRef(null);

  const formatResponse = (text) => {
    if (!text) return '';
    return text
      .replace(/### (.*?)\n/g, '<h3>$1</h3>')
      .replace(/## (.*?)\n/g, '<h2>$1</h2>')
      .replace(/# (.*?)\n/g, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br />');
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) {
      setMessage('Không có tệp nào được chọn.');
      setImage(null);
      setPreview(null);
      setResponse(null);
      setError(null);
      return;
    }

    if (!file.type.startsWith('image/')) {
      setMessage('Vui lòng chọn một tệp hình ảnh.');
      setImage(null);
      setPreview(null);
      setResponse(null);
      setError(null);
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setMessage('Hình ảnh quá lớn (tối đa 5MB).');
      setImage(null);
      setPreview(null);
      setResponse(null);
      setError(null);
      return;
    }

    setImage(file);
    setPreview(URL.createObjectURL(file));
    setMessage(`Đã chọn hình ảnh: ${file.name}`);
    setResponse(null);
    setError(null);
  };

  const handleClear = () => {
    setImage(null);
    setPreview(null);
    setMessage(null);
    setResponse(null);
    setError(null);
    if (preview) URL.revokeObjectURL(preview);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = async () => {
    if (!image) {
      setMessage('Vui lòng chọn một hình ảnh.');
      setError('Không có hình ảnh để gửi.');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    formData.append('file', image);
    formData.append('detail_level', detailLevel); // Send detail level to backend

    try {
      const res = await axios.post('http://localhost:8000/herb/identify', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResponse(res.data);
      setMessage('Đã nhận diện cây thuốc.');
    } catch (err) {
      setError(err.response?.data?.answer || 'Đã xảy ra lỗi khi nhận diện hình ảnh.');
      setMessage('Không thể xử lý hình ảnh.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.uploadBox}>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          style={styles.fileInput}
          id="image-upload"
          ref={fileInputRef}
        />
        <label htmlFor="image-upload" style={styles.uploadLabel}>
          <BiImageAdd style={styles.uploadIcon} />
          {image ? 'Chọn ảnh khác' : 'Chọn ảnh cây thuốc'}
        </label>
        {image && (
          <>
            <div style={styles.radioGroup}>
              <label style={styles.radioLabel}>
                <input
                  type="radio"
                  value="tóm tắt"
                  checked={detailLevel === 'tóm tắt'}
                  onChange={(e) => setDetailLevel(e.target.value)}
                  style={styles.radioInput}
                />
                Tóm tắt
              </label>
              <label style={styles.radioLabel}>
                <input
                  type="radio"
                  value="đầy đủ"
                  checked={detailLevel === 'đầy đủ'}
                  onChange={(e) => setDetailLevel(e.target.value)}
                  style={styles.radioInput}
                />
                Đầy đủ
              </label>
              <label style={styles.radioLabel}>
                <input
                  type="radio"
                  value="chi tiết"
                  checked={detailLevel === 'chi tiết'}
                  onChange={(e) => setDetailLevel(e.target.value)}
                  style={styles.radioInput}
                />
                Chi tiết
              </label>
            </div>
            <button
              onClick={handleSubmit}
              disabled={loading}
              style={{ ...styles.submitButton, opacity: loading ? 0.6 : 1 }}
            >
              {loading ? 'Đang xử lý...' : 'Gửi ảnh'}
            </button>
            <button onClick={handleClear} style={styles.clearButton}>
              Xóa ảnh
            </button>
          </>
        )}
      </div>

      {preview && (
        <div style={styles.previewBox}>
          <img src={preview} alt="Herb Preview" style={styles.previewImage} />
        </div>
      )}

      {(message || response || error) && (
        <div style={styles.responseBox}>
          {message && (
            <>
              <strong style={styles.responseLabel}>Thông báo:</strong>
              <p style={styles.responseText}>{message}</p>
            </>
          )}
          {error && (
            <>
              <strong style={styles.responseLabel}>Lỗi:</strong>
              <p style={{ ...styles.responseText, color: '#d32f2f' }}>{error}</p>
            </>
          )}
          {response && !error && ( // Only show result if there's a response and no error
            <>
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
              {response.herb_code && (
                <div style={styles.herbsPageBox}>
                  <HerbsPage selectedCode={response.herb_code} hasAnswer={true} />
                </div>
              )}
              <button
                style={{ ...styles.submitButton, background: 'linear-gradient(to right, #81c784, #66bb6a)', marginTop: '15px' }}
                onClick={() => setShowFeedback(!showFeedback)}
              >
                {showFeedback ? 'Ẩn Phản Hồi' : 'Gửi Phản Hồi'}
              </button>

              {showFeedback && (
                <div style={styles.feedbackBox}>
                  <FeedbackPage />
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

const styles = {
  wrapper: {
    background: 'var(--card-background)',
    padding: '30px',
    borderRadius: '12px',
    boxShadow: '0 4px 12px var(--shadow-color)',
    animation: 'fadeInUp 0.5s ease-in-out',
    maxWidth: '600px',
    margin: '40px auto',
  },
  uploadBox: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '15px',
  },
  fileInput: {
    display: 'none',
  },
  uploadLabel: {
    padding: '12px 14px',
    borderRadius: '8px',
    background: 'linear-gradient(to right, #81c784, #66bb6a)',
    color: '#fff',
    fontWeight: 'bold',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    transition: 'background 0.3s',
    fontSize: '16px',
    fontFamily: "'Be Vietnam Pro', sans-serif",
  },
  uploadIcon: {
    marginRight: '6px',
    fontSize: '18px',
  },
  submitButton: {
    padding: '12px 14px',
    borderRadius: '8px',
    background: 'var(--primary-color)',
    color: '#fff',
    fontWeight: 'bold',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    fontFamily: "'Be Vietnam Pro', sans-serif",
    transition: 'opacity 0.3s',
  },
  previewBox: {
    marginTop: '15px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '15px',
  },
  previewImage: {
    maxWidth: '100%',
    maxHeight: '200px',
    borderRadius: '10px',
    border: '1px solid var(--border-color)',
    objectFit: 'contain',
  },
  clearButton: {
    padding: '12px 14px',
    borderRadius: '8px',
    background: '#ef5350',
    color: '#fff',
    fontWeight: 'bold',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    fontFamily: "'Be Vietnam Pro', sans-serif",
  },
  responseBox: {
    marginTop: '30px',
    paddingTop: '20px',
    borderTop: '1px solid var(--border-color)',
  },
  responseLabel: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: 'var(--primary-color)',
    marginBottom: '10px',
  },
  responseText: {
    lineHeight: '1.8',
    fontSize: '16px',
    marginBottom: '20px',
  },
  radioGroup: {
    display: 'flex',
    gap: '20px',
    marginTop: '10px',
    marginBottom: '10px',
  },
  radioLabel: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '16px',
    fontFamily: "'Be Vietnam Pro', sans-serif",
    color: 'var(--text-color)',
    cursor: 'pointer',
  },
  radioInput: {
    marginRight: '8px',
    transform: 'scale(1.2)',
  },
  herbsPageBox: {
    marginTop: '30px',
  },
  feedbackBox: { // Add this style
    marginTop: '30px',
  },
};

export default ImageUpload;
