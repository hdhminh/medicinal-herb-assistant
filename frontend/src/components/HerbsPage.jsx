import React, { useState, useEffect } from 'react';

const HerbsPage = () => {
  const [herbs, setHerbs] = useState([]);
  const [expandedHerbId, setExpandedHerbId] = useState(null);
  const [error, setError] = useState(null);

  // Placeholder image
  const placeholderImage = 'https://images.unsplash.com/photo-1598511726619-6f57f43fc246?w=300';

  // Fetch herbs from backend
  useEffect(() => {
    fetch('http://localhost:8000/herb/list')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch herbs data');
        }
        return response.json();
      })
      .then(data => {
        setHerbs(data.map(herb => ({
          ...herb,
          image_url: `/images/${herb.code}.jpg`
        })));
      })
      .catch(error => {
        console.error('Error loading herbs:', error);
        setError('Không thể tải danh sách cây thuốc. Vui lòng thử lại sau.');
      });
  }, []);

  const handleToggle = (id) => {
    setExpandedHerbId(expandedHerbId === id ? null : id);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Loại Cây Thuốc</h2>
      {error ? (
        <p style={styles.text}>{error}</p>
      ) : herbs.length === 0 ? (
        <p style={styles.text}>Đang tải dữ liệu...</p>
      ) : (
        <div style={styles.grid}>
          {herbs.map((herb) => (
            <div key={herb.id} style={styles.card}>
              <div style={styles.cardInner} onClick={() => handleToggle(herb.id)}>
                <img
                  src={herb.image_url}
                  alt={herb.name}
                  style={styles.image}
                  onError={(e) => { e.target.src = placeholderImage; }}
                />
                <h3 style={styles.caption}>{herb.name}</h3>
              </div>
              {expandedHerbId === herb.id && (
                <div style={styles.details}>
                  <p><strong>Tên khoa học:</strong> {herb.scientific_name}</p>
                  <p><strong>Mô tả:</strong> {herb.description}</p>
                  <p><strong>Công dụng:</strong> {herb.uses}</p>
                </div>
              )}
            </div>
          ))}
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
    padding: '30px',
  },
  title: {
    fontSize: '28px',
    color: '#2e7d32',
    marginBottom: '20px',
    textAlign: 'center',
  },
  text: {
    fontSize: '16px',
    color: '#555',
    textAlign: 'center',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
    width: '100%',
    maxWidth: '1200px',
  },
  card: {
    background: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    overflow: 'hidden',
    cursor: 'pointer',
    transition: 'transform 0.3s, box-shadow 0.3s',
  },
  cardInner: {
    padding: '10px',
    textAlign: 'center',
  },
  image: {
    width: '100%',
    height: '150px',
    objectFit: 'cover',
    borderRadius: '4px',
  },
  caption: {
    fontSize: '18px',
    color: '#333',
    margin: '10px 0 0',
  },
  details: {
    padding: '15px',
    background: '#f9f9f9',
    fontSize: '14px',
    color: '#555',
    borderTop: '1px solid #eee',
  },
};

export default HerbsPage;