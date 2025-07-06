import React, { useState } from 'react';
import { BiImageAdd } from 'react-icons/bi';

const ImageUpload = () => {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [message, setMessage] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setMessage('Vui lòng chọn một tệp hình ảnh.');
        setImage(null);
        setPreview(null);
        setResponse(null);
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setMessage('Hình ảnh quá lớn (tối đa 5MB).');
        setImage(null);
        setPreview(null);
        setResponse(null);
        return;
      }
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setMessage(`Đã chọn hình ảnh: ${file.name}`);
      setResponse(null);
      setError(null);
    }
  };

  const handleClear = () => {
    setImage(null);
    setPreview(null);
    setMessage(null);
    setResponse(null);
    setError(null);
    if (preview) URL.revokeObjectURL(preview);
  };

  const handleSubmit = async () => {
    if (!image) {
      setMessage('Vui lòng chọn một hình ảnh.');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    formData.append('file', image);

    try {
      const res = await fetch('http://localhost:8000/herb/identify', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Lỗi: ${res.status} - ${await res.text()}`);
      }

      const data = await res.json();
      setResponse(data);
      setMessage('Đã nhận thông tin cây thuốc.');
    } catch (err) {
      setError(err.message);
      setMessage('Đã xảy ra lỗi khi gửi hình ảnh.');
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
        />
        <label htmlFor="image-upload" style={styles.uploadLabel}>
          <BiImageAdd style={styles.uploadIcon} />
          {image ? 'Chọn ảnh khác' : 'Chọn ảnh cây thuốc'}
        </label>
        {image && (
          <button onClick={handleSubmit} style={styles.submitButton} disabled={loading}>
            {loading ? 'Đang xử lý...' : 'Gửi ảnh'}
          </button>
        )}
      </div>

      {preview && (
        <div style={styles.previewBox}>
          <img src={preview} alt="Herb Preview" style={styles.previewImage} />
          <button onClick={handleClear} style={styles.clearButton}>
            Xóa ảnh
          </button>
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
          {response && (
            <>
              <strong style={styles.responseLabel}>Kết quả:</strong>
              <p style={styles.responseText}>{response.answer}</p>
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
            </>
          )}
        </div>
      )}
    </div>
  );
};

const styles = {
  wrapper: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    animation: 'fadeIn 0.5s ease-in-out',
  },
  uploadBox: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
  },
  fileInput: {
    display: 'none',
  },
  uploadLabel: {
    padding: '10px 14px',
    borderRadius: '10px',
    background: 'linear-gradient(to right, #81c784, #66bb6a)',
    color: '#fff',
    fontWeight: 'bold',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    transition: 'background 0.3s',
  },
  uploadIcon: {
    marginRight: '6px',
    fontSize: '18px',
  },
  submitButton: {
    padding: '8px 12px',
    borderRadius: '8px',
    background: '#1976d2',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    opacity: (props) => (props.disabled ? 0.6 : 1),
  },
  previewBox: {
    marginTop: '12px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
  },
  previewImage: {
    maxWidth: '100%',
    maxHeight: '200px',
    borderRadius: '10px',
    border: '1px solid #ccc',
    objectFit: 'contain',
  },
  clearButton: {
    padding: '8px 12px',
    borderRadius: '8px',
    background: '#ef5350',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
  },
  responseBox: {
    marginTop: '20px',
    backgroundColor: '#f1f8e9',
    padding: '18px',
    borderRadius: '10px',
    boxShadow: '0 3px 10px rgba(0,0,0,0.1)',
  },
  responseLabel: {
    display: 'block',
    marginBottom: '10px',
    fontSize: '18px',
    color: '#33691e',
  },
  responseText: {
    lineHeight: '1.7',
    fontSize: '16px',
    color: '#333',
  },
};

export default ImageUpload;