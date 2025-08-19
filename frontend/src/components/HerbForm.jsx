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
  const [answerType, setAnswerType] = useState('tóm tắt');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

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

  const handleAsk = async () => {
    if (!code || !question) {
      setResponse({
        answer: '[Lỗi] Vui lòng chọn mã cây thuốc và nhập câu hỏi.',
        source: null,
      });
      setLoading(false);
      return;
    }

    setLoading(true);
    setResponse(null);
    try {
      const res = await axios.post('http://localhost:8000/herb/ask', { code, question, answer_type: answerType });
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

      <div style={styles.radioGroup}>
        <label style={styles.radioLabel}>
          <input
            type="radio"
            value="tóm tắt"
            checked={answerType === 'tóm tắt'}
            onChange={(e) => setAnswerType(e.target.value)}
            style={styles.radioInput}
          />
          Tóm tắt
        </label>
        <label style={styles.radioLabel}>
          <input
            type="radio"
            value="đầy đủ"
            checked={answerType === 'đầy đủ'}
            onChange={(e) => setAnswerType(e.target.value)}
            style={styles.radioInput}
          />
          Đầy đủ
        </label>
        <label style={styles.radioLabel}>
          <input
            type="radio"
            value="chi tiết"
            checked={answerType === 'chi tiết'}
            onChange={(e) => setAnswerType(e.target.value)}
            style={styles.radioInput}
          />
          Chi tiết
        </label>
      </div>

      <button onClick={handleAsk} disabled={loading || !code || !question} style={styles.button}>
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

      {response && response.answer && response.answer !== '[Lỗi] Không thể lấy dữ liệu từ máy chủ.' && response.answer !== '[Lỗi] Vui lòng chọn mã cây thuốc và nhập câu hỏi.' && (
        <>
          <div style={styles.responseBox}>
            <strong style={styles.responseLabel}>Kết quả:</strong>
            <p
              style={styles.responseText}
              dangerouslySetInnerHTML={{ __html: formatResponse(response.answer) }}
            />
            <div style={styles.sourceContainer}>
              {response.source && (
                <div>
                  <strong style={styles.sourceLabel}>Nguồn:</strong>
                  <p style={styles.sourceText}>
                    <a href={response.source} target="_blank" rel="noopener noreferrer">
                      {response.source_title || response.source}
                    </a>
                  </p>
                </div>
              )}
            </div>
          </div>

          <div style={styles.herbsPageBox}>
            <HerbsPage selectedCode={code} hasAnswer={true} />
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

      {response && response.answer && (response.answer === '[Lỗi] Không thể lấy dữ liệu từ máy chủ.' || response.answer === '[Lỗi] Vui lòng chọn mã cây thuốc và nhập câu hỏi.') && (
        <div style={styles.responseBox}>
          <strong style={styles.responseLabel}>Lỗi:</strong>
          <p style={{ ...styles.responseText, color: '#d32f2f' }}>{response.answer}</p>
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
  textarea: {
    width: '100%',
    padding: '12px',
    borderRadius: '8px',
    border: '1px solid var(--border-color)',
    fontSize: '16px',
    outline: 'none',
    transition: 'all 0.3s',
    resize: 'vertical',
    boxSizing: 'border-box',
    marginTop: '15px',
    fontFamily: "'Be Vietnam Pro', sans-serif",
  },
  button: {
    width: '100%',
    padding: '12px',
    borderRadius: '8px',
    background: 'var(--primary-color)',
    color: '#fff',
    fontWeight: 'bold',
    border: 'none',
    cursor: 'pointer',
    transition: 'background 0.3s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: '15px',
    fontSize: '16px',
  },
  feedbackBox: {
    marginTop: '30px',
  },
  herbsPageBox: {
    marginTop: '30px',
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
  sourceContainer: {
    marginTop: '20px',
    paddingTop: '15px',
    borderTop: '1px solid var(--border-color)',
  },
  sourceLabel: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: 'var(--primary-color)',
  },
  sourceText: {
    fontSize: '14px',
    color: '#555',
  },
  radioGroup: {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: '20px',
    margin: '20px 0',
  },
  radioLabel: {
    display: 'flex',
    alignItems: 'center',
    cursor: 'pointer',
    fontSize: '16px',
  },
  radioInput: {
    marginRight: '8px',
  },
};

const customSelectStyles = {
  control: (base) => ({
    ...base,
    borderRadius: '8px',
    padding: '4px',
    fontSize: '16px',
    borderColor: 'var(--border-color)',
    boxShadow: 'none',
    '&:hover': { borderColor: 'var(--primary-color)' },
  }),
  menu: (base) => ({
    ...base,
    borderRadius: '8px',
    zIndex: 100,
  }),
  option: (base, { isFocused }) => ({
    ...base,
    backgroundColor: isFocused ? 'var(--background-color)' : 'var(--card-background)',
    color: 'var(--text-color)',
    fontSize: '16px',
  }),
};

export default HerbForm;
