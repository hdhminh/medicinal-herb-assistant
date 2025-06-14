import React from 'react';
import HerbForm from './components/HerbForm';
import './App.css';
import { GiMedicines } from 'react-icons/gi';


function App() {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>
          <GiMedicines style={{ marginRight: '10px', color: '#43a047' }} />
          Hệ thống hỏi đáp dược liệu
        </h1>
        <p style={styles.subtitle}>Nhập mã cây và câu hỏi để nhận câu trả lời từ AI</p>
        <HerbForm />
      </div>
    </div>
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
};

export default App;
