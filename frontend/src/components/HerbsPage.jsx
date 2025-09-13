import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { FiImage } from 'react-icons/fi';

const HerbsPage = ({ selectedCode, hasAnswer }) => {
  const [herbs, setHerbs] = useState([]);
  const [error, setError] = useState(null);
  const [herbImages, setHerbImages] = useState({});
  const [visibleImages, setVisibleImages] = useState({});
  const [moreClicks, setMoreClicks] = useState({});
  const maxClicks = 3;
  const imagesPerClick = 5;
  const maxTotalImages = 20;
  const placeholderImage = 'https://images.unsplash.com/photo-1598511726619-6f57f43fc246?w=300';

  const fetchHerbData = useCallback(async () => {
    try {
      const response = await axios.get(`http://localhost:8000/herb/list`);
      const herbData = Array.isArray(response.data) ? response.data : [response.data];
      const filteredHerbs = herbData.filter(herb => herb.code === selectedCode);
      if (filteredHerbs.length === 0) {
        setError('Không tìm thấy thông tin cây thuốc.');
        setHerbs([]);
        return;
      }
      const formattedHerbs = filteredHerbs.map(herb => ({
        ...herb,
        image_url: herb.image_url || placeholderImage,
      }));
      setHerbs(formattedHerbs);
      if (formattedHerbs.length > 0) {
        await fetchHerbImages(formattedHerbs[0].id, selectedCode);
      }
    } catch (error) {
      console.error('Error loading herb:', error);
      setError('Không thể tải thông tin cây thuốc. Vui lòng thử lại sau.');
      setHerbs([]);
      setHerbImages({});
      setVisibleImages({});
      setMoreClicks({});
    }
  }, [selectedCode]);

  const fetchHerbImages = useCallback(async (herbId, code) => {
    try {
      const imageRes = await axios.get(`http://localhost:8000/herb/${code}/images?limit=${imagesPerClick}`);
      const images = imageRes.data || [];
      

      if (images.length > 0) {
        setHerbs(prevHerbs => prevHerbs.map(h => 
          h.code === code ? { ...h, image_url: images[0] } : h
        ));
      }

      const initialImages = images.slice(0, imagesPerClick);
      const paddedImages = [
        ...initialImages,
        ...Array(Math.max(0, imagesPerClick - initialImages.length)).fill(placeholderImage),
      ].slice(0, imagesPerClick);
      setHerbImages(prev => ({
        ...prev,
        [herbId]: paddedImages,
      }));
      setVisibleImages(prev => ({
        ...prev,
        [herbId]: paddedImages,
      }));
      setMoreClicks(prev => ({ ...prev, [herbId]: 0 }));
    } catch (imageError) {
      console.error(`Error fetching images for herb ${code}:`, imageError);
      setHerbImages(prev => ({
        ...prev,
        [herbId]: Array(imagesPerClick).fill(placeholderImage),
      }));
      setVisibleImages(prev => ({
        ...prev,
        [herbId]: Array(imagesPerClick).fill(placeholderImage),
      }));
      setMoreClicks(prev => ({ ...prev, [herbId]: 0 }));
    }
  }, [herbs]);

  const handleMorePictures = useCallback(async (herbId, code) => {
    const currentClicks = moreClicks[herbId] || 0;
    if (currentClicks >= maxClicks) return;

    try {
      const offset = (currentClicks + 1) * imagesPerClick;
      const imageRes = await axios.get(`http://localhost:8000/herb/${code}/images?limit=${imagesPerClick}&offset=${offset}`);
      const newImages = imageRes.data || [];
      const paddedImages = [
        ...newImages,
        ...Array(Math.max(0, imagesPerClick - newImages.length)).fill(placeholderImage),
      ].slice(0, imagesPerClick);
      setHerbImages(prev => ({
        ...prev,
        [herbId]: [...prev[herbId], ...paddedImages].slice(0, maxTotalImages),
      }));
      setVisibleImages(prev => ({
        ...prev,
        [herbId]: [...prev[herbId], ...paddedImages].slice(0, (currentClicks + 2) * imagesPerClick),
      }));
      setMoreClicks(prev => ({
        ...prev,
        [herbId]: currentClicks + 1,
      }));
    } catch (imageError) {
      console.error(`Error fetching more images for herb ${code}:`, imageError);
      const paddedImages = Array(imagesPerClick).fill(placeholderImage);
      setHerbImages(prev => ({
        ...prev,
        [herbId]: [...prev[herbId], ...paddedImages].slice(0, maxTotalImages),
      }));
      setVisibleImages(prev => ({
        ...prev,
        [herbId]: [...prev[herbId], ...paddedImages].slice(0, (currentClicks + 2) * imagesPerClick),
      }));
      setMoreClicks(prev => ({
        ...prev,
        [herbId]: currentClicks + 1,
      }));
    }
  }, [moreClicks]);

  useEffect(() => {
    if (selectedCode && hasAnswer) {
      fetchHerbData();
    } else {
      setHerbs([]);
      setHerbImages({});
      setVisibleImages({});
      setMoreClicks({});
      setError(null);
    }
  }, [selectedCode, hasAnswer, fetchHerbData]);

  if (!hasAnswer || !selectedCode) {
    return null;
  }

  return (
    <div style={styles.container}>
      {error ? (
        <p style={styles.text}>{error}</p>
      ) : herbs.length === 0 ? (
        <p style={styles.text}>Không có dữ liệu cây thuốc.</p>
      ) : (
        <div style={styles.grid}>
          {herbs.map(herb => (
            <div key={herb.id} style={styles.card}>
              <img
                src={herb.image_url}
                alt={herb.name}
                style={styles.image}
                onError={(e) => { e.target.src = placeholderImage; }}
              />
              <div style={styles.cardContent}>
                <h3 style={styles.caption}>{herb.name}</h3>
                <div style={styles.details}>
                  <p><strong>Tên khoa học:</strong> {herb.scientific_name || 'Không có dữ liệu'}</p>
                  <p><strong>Mô tả:</strong> {herb.description || 'Không có mô tả'}</p>
                  <p><strong>Công dụng:</strong> {herb.uses || 'Không có công dụng'}</p>
                </div>
                {visibleImages[herb.id] && (
                  <div style={styles.imageGrid}>
                    {visibleImages[herb.id].map((img, index) => (
                      <img
                        key={index}
                        src={img}
                        alt={`Herb ${herb.name} ${index + 1}`}
                        style={styles.herbImage}
                        onError={(e) => { e.target.src = placeholderImage; }}
                      />
                    ))}
                  </div>
                )}
                {moreClicks[herb.id] < maxClicks && (
                  <button
                    style={styles.moreButton}
                    onClick={() => handleMorePictures(herb.id, herb.code)}
                  >
                    <FiImage style={styles.inlineIcon} />
                    Xem thêm hình ảnh
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    width: '100%',
    maxWidth: '700px',
    margin: '0 auto',
  },
  text: {
    fontSize: '16px',
    color: '#555',
    textAlign: 'center',
  },
  grid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  card: {
    background: '#fff',
    borderRadius: '12px',
    overflow: 'hidden',
    boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
  },
  cardContent: {
    padding: '20px',
  },
  image: {
    width: '100%',
    height: '220px',
    objectFit: 'cover',
  },
  caption: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#2e7d32',
    margin: '0 0 15px',
    borderBottom: '2px solid #e0e0e0',
    paddingBottom: '10px',
  },
  details: {
    fontSize: '16px',
    color: '#333',
    lineHeight: '1.7',
  },
  imageGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))',
    gap: '10px',
    marginTop: '15px',
  },
  herbImage: {
    width: '100%',
    height: '100px',
    objectFit: 'cover',
    borderRadius: '4px',
    border: '1px solid #ccc',
  },
  moreButton: {
    padding: '8px 12px',
    borderRadius: '8px',
    background: 'linear-gradient(to right, #4caf50, #388e3c)',
    color: '#fff',
    fontWeight: 'bold',
    border: 'none',
    cursor: 'pointer',
    marginTop: '15px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  inlineIcon: {
    marginRight: '6px',
    verticalAlign: 'middle',
  },
};

export default HerbsPage;
