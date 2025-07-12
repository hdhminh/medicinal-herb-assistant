import React, { useState } from 'react';
import axios from 'axios';
import { herbCodes } from '../constants/herbCodes';
import Select from 'react-select';
import { FaRocket } from 'react-icons/fa';
import { AiOutlineLoading3Quarters } from 'react-icons/ai';
import HerbsPage from './HerbsPage';
import FeedbackPage from './FeedbackPage';

const HerbForm = () => {
  const [code, setCode] = useState('');
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  const handleAsk = async () => {
    setLoading(true);
    setResponse(null);
    try {
      const res = await axios.post('http://localhost:8000/herb/ask', { code, question });
      setResponse(res.data);
    } catch (err) {
      setResponse({
        answer: '[Lỗi] Không thể lấy dữ liệu từ máy chủ.',
        source: null,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.wrapper}>
      <Select
        options={herbCodes.map((item) => ({
          value: item.code,
          label: `${item.code} - ${item.name}`,
        }))}
        onChange={(selected) => setCode(selected?.value || '')}
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

      <button onClick={handleAsk} disabled={loading} style={styles.button}>
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

      {response && response.answer && (
        <>
          <div style={styles.herbsPageBox}>
            <HerbsPage selectedCode={code} hasAnswer={!!response && !!response.answer} />
          </div>

          <button
            style={{ ...styles.button, background: 'linear-gradient(to right, #81c784, #66bb6a)' }}
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
  );
};

const styles = {
  wrapper: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    animation: 'fadeIn 0.5s ease-in-out',
  },
  input: {
    padding: '10px 14px',
    borderRadius: '10px',
    border: '1px solid #ccc',
    fontSize: '16px',
    outline: 'none',
    transition: 'all 0.3s',
  },
  textarea: {
    padding: '10px 14px',
    borderRadius: '10px',
    border: '1px solid #ccc',
    fontSize: '16px',
    outline: 'none',
    transition: 'all 0.3s',
    resize: 'vertical',
  },
  button: {
    padding: '10px',
    borderRadius: '10px',
    background: 'linear-gradient(to right, #66bb6a, #43a047)',
    color: '#fff',
    fontWeight: 'bold',
    border: 'none',
    cursor: 'pointer',
    transition: 'background 0.3s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  feedbackBox: {
    marginTop: '20px',
    backgroundColor: '#f1f8e9',
    padding: '18px',
    borderRadius: '10px',
    boxShadow: '0 3px 10px rgba(0,0,0,0.1)',
  },
  herbsPageBox: {
    marginTop: '20px',
    backgroundColor: '#f1f8e9',
    padding: '18px',
    borderRadius: '10px',
    boxShadow: '0 3px 10px rgba(0,0,0,0.1)',
  },
};

const customSelectStyles = {
  control: (base) => ({
    ...base,
    borderRadius: '10px',
    padding: '3px 6px',
    fontSize: '16px',
    borderColor: '#ccc',
    boxShadow: 'none',
    '&:hover': { borderColor: '#66bb6a' },
  }),
  menu: (base) => ({
    ...base,
    borderRadius: '10px',
    zIndex: 100,
  }),
  option: (base, { isFocused }) => ({
    ...base,
    backgroundColor: isFocused ? '#e0f2f1' : 'white',
    color: '#333',
    fontSize: '15px',
    padding: '10px 12px',
  }),
};

export default HerbForm;