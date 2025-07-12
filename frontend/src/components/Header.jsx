import React from 'react';
import { NavLink } from 'react-router-dom';
import { GiMedicines } from 'react-icons/gi';

const Header = () => {
  return (
    <header style={styles.header}>
      <div style={styles.logo}>
        <GiMedicines style={styles.logoIcon} />
        <span style={styles.logoText}>Hệ thống hỏi đáp dược liệu</span>
      </div>
      
    </header>
  );
};

const styles = {
  header: {
    background: 'linear-gradient(to right, #66bb6a, #43a047)',
    color: '#fff',
    padding: '15px 30px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 2px 5px rgba(0, 0, 0, 0.2)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  logoIcon: {
    fontSize: '28px',
  },
  logoText: {
    fontSize: '20px',
    fontWeight: 'bold',
  },
  nav: {
    display: 'flex',
    gap: '20px',
  },
  navLink: {
    color: '#fff',
    textDecoration: 'none',
    fontSize: '16px',
    fontWeight: '500',
    padding: '8px 12px',
    borderRadius: '5px',
    transition: 'background 0.3s',
  },
  activeLink: {
    backgroundColor: '#2e7d32',
  },
};

export default Header;
