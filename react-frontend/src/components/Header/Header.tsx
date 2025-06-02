import React from 'react';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="32" height="32" rx="8" fill="#007bff"/>
              <path d="M8 12h16v2H8v-2zm0 4h16v2H8v-2zm0 4h12v2H8v-2z" fill="white"/>
            </svg>
          </div>
          <div className="header-text">
            <h1>Contract Redlining</h1>
            <p>AI-powered risk assessment • Powered by MISTRAL7b</p>
          </div>
        </div>
        
        <div className="header-right">
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>System Ready</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 