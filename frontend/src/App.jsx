import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HerbForm from './components/HerbForm';
import ImageUpload from './components/ImageUpload';
import HerbsPage from './components/HerbsPage';
import FeedbackPage from './components/FeedbackPage';
import './App.css';
import { GiMedicines } from 'react-icons/gi';

function App() {
  return (
    <BrowserRouter>
      <Header />
      <div style={styles.container}>
        <Routes>
          <Route
            path="/"
            element={
              <div style={styles.card}>
                <h1 style={styles.title}>
                  <GiMedicines style={{ marginRight: '10px', color: '#43a047' }} />
                  Hệ thống hỏi đáp dược liệu
                </h1>
                <p style={styles.subtitle}>Nhập mã cây, câu hỏi hoặc chọn ảnh để xem trước</p>
                <HerbForm />
                <hr style={styles.divider} />
                <h2 style={styles.sectionTitle}>Xem trước ảnh cây thuốc</h2>
                <ImageUpload />
              </div>
            }
          />
          <Route path="/herbs" element={<HerbsPage />} />
          <Route path="/feedback" element={<FeedbackPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #e8f5e9, #f1f8e9)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '30px',
  },
  card: {
    backgroundColor: '#ffffff',
    padding: '32px',
    borderRadius: '20px',
    boxShadow: '0 15px 30px rgba(0, 0, 0, 0.1)',
    maxWidth: '640px',
    width: '100%',
    animation: 'fadeInUp 0.6s ease-in-out',
  },
  title: {
    marginBottom: '10px',
    fontSize: '28px',
    textAlign: 'center',
    color: '#2e7d32',
  },
  subtitle: {
    marginBottom: '20px',
    textAlign: 'center',
    color: '#555',
  },
  divider: {
    border: '1px solid #e0e0e0',
    margin: '20px 0',
  },
  sectionTitle: {
    fontSize: '22px',
    color: '#2e7d32',
    textAlign: 'center',
    marginBottom: '20px',
  },
};

export default App;