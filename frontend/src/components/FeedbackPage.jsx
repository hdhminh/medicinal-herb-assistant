import React, { useState } from 'react';
import { BiImageAdd } from 'react-icons/bi';

const FeedbackPage = () => {
  const [feedbackType, setFeedbackType] = useState('');
  const [comments, setComments] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [otherDetails, setOtherDetails] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFeedbackTypeChange = (e) => {
    setFeedbackType(e.target.value);
    setOtherDetails(''); 
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setMessage('Vui lòng chọn một tệp hình ảnh.');
        setImage(null);
        setPreview(null);
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setMessage('Hình ảnh quá lớn (tối đa 5MB).');
        setImage(null);
        setPreview(null);
        return;
      }
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setMessage(`Đã chọn hình ảnh: ${file.name}`);
    }
  };

  const handleClearImage = () => {
    setImage(null);
    setPreview(null);
    setMessage('');
    if (preview) URL.revokeObjectURL(preview);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    if (!feedbackType || !comments) {
      setMessage('Vui lòng chọn loại phản hồi và nhập nội dung.');
      setLoading(false);
      return;
    }

    if (feedbackType === 'Other' && !otherDetails) {
      setMessage('Vui lòng nhập chi tiết cho loại phản hồi "Khác".');
      setLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append('feedback_type', feedbackType);
    formData.append('comments', comments);
    formData.append('user_email', userEmail || '');
    formData.append('other_details', otherDetails || '');
    if (image) {
      formData.append('image', image);
    }

    try {
      const response = await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Lỗi: ${response.status} - ${await response.text()}`);
      }

      const data = await response.json();
      setMessage(data.message || 'Phản hồi đã được gửi thành công!');
      setFeedbackType('');
      setComments('');
      setUserEmail('');
      setOtherDetails('');
      setImage(null);
      setPreview(null);
      if (preview) URL.revokeObjectURL(preview);
    } catch (error) {
      setMessage(`Lỗi khi gửi phản hồi: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Phản Hồi</h2>
      <form style={styles.form} onSubmit={handleSubmit}>
        <div style={styles.formGroup}>
          <label style={styles.label}>Loại Phản Hồi:</label>
          <div style={styles.radioGroup}>
            <label style={styles.radioLabel}>
              <input
                type="radio"
                value="Wrong Prediction"
                checked={feedbackType === 'Wrong Prediction'}
                onChange={handleFeedbackTypeChange}
                style={styles.radio}
              />
              Dự đoán sai
            </label>
            <label style={styles.radioLabel}>
              <input
                type="radio"
                value="Wrong Data"
                checked={feedbackType === 'Wrong Data'}
                onChange={handleFeedbackTypeChange}
                style={styles.radio}
              />
              Dữ liệu sai
            </label>
            <label style={styles.radioLabel}>
              <input
                type="radio"
                value="Other"
                checked={feedbackType === 'Other'}
                onChange={handleFeedbackTypeChange}
                style={styles.radio}
              />
              Khác
            </label>
          </div>
        </div>

        {feedbackType === 'Other' && (
          <div style={styles.formGroup}>
            <label style={styles.label}>Chi tiết loại phản hồi "Khác":</label>
            <textarea
              value={otherDetails}
              onChange={(e) => setOtherDetails(e.target.value)}
              style={styles.textarea}
              placeholder="Vui lòng mô tả chi tiết loại phản hồi khác..."
              required
            />
          </div>
        )}

        <div style={styles.formGroup}>
          <label style={styles.label}>Email (Tùy chọn):</label>
          <input
            type="email"
            value={userEmail}
            onChange={(e) => setUserEmail(e.target.value)}
            style={styles.input}
            placeholder="Nhập email nếu bạn muốn nhận phản hồi"
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Hình Ảnh Thử Nghiệm (Tùy chọn):</label>
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
              {image ? 'Chọn ảnh khác' : 'Chọn ảnh thử nghiệm'}
            </label>
          </div>
          {preview && (
            <div style={styles.previewBox}>
              <img src={preview} alt="Preview" style={styles.previewImage} />
              <button type="button" onClick={handleClearImage} style={styles.clearButton}>
                Xóa ảnh
              </button>
            </div>
          )}
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Giải thích lỗi sai thêm chi tiết:</label>
          <textarea
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            style={styles.textarea}
            placeholder="Vui lòng mô tả chi tiết lỗi hoặc vấn đề bạn gặp phải..."
            required
          />
        </div>

        <button type="submit" style={styles.button} disabled={loading}>
          {loading ? 'Đang gửi...' : 'Gửi Phản Hồi'}
        </button>
      </form>

      {message && (
        <div
          style={{
            ...styles.message,
            color: message.includes('Lỗi') ? '#d32f2f' : '#2e7d32',
          }}
        >
          {message}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #e8f5e9, #f1f8e9)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '30px',
  },
  title: {
    fontSize: '28px',
    color: '#2e7d32',
    marginBottom: '20px',
    textAlign: 'center',
  },
  form: {
    background: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    width: '100%',
    maxWidth: '500px',
  },
  formGroup: {
    marginBottom: '15px',
  },
  label: {
    display: 'block',
    fontSize: '16px',
    color: '#333',
    marginBottom: '5px',
  },
  radioGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  radioLabel: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '16px',
    color: '#333',
  },
  radio: {
    marginRight: '8px',
  },
  textarea: {
    width: '100%',
    padding: '8px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '16px',
    minHeight: '100px',
  },
  input: {
    width: '100%',
    padding: '8px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '16px',
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
  button: {
    padding: '10px 20px',
    borderRadius: '8px',
    background: '#2e7d32',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    width: '100%',
    opacity: (props) => (props.disabled ? 0.6 : 1),
  },
  message: {
    marginTop: '15px',
    fontSize: '16px',
    textAlign: 'center',
  },
};

export default FeedbackPage;
