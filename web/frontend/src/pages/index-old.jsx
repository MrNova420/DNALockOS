/**
 * =============================================================================
 * DNALockOS - DNA-Key Authentication System
 * Copyright (c) 2025 WeNova Interactive
 * =============================================================================
 *
 * OWNERSHIP AND LEGAL NOTICE:
 *
 * This software and all associated intellectual property is the exclusive
 * property of WeNova Interactive, legally owned and operated by:
 *
 *     Kayden Shawn Massengill
 *
 * COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE
 *
 * This is proprietary commercial software. It is NOT free software. It is NOT
 * open source software. This software is developed for commercial sale and
 * requires a valid commercial license for ANY use.
 *
 * STRICT PROHIBITION NOTICE:
 *
 * Without a valid commercial license agreement, you are PROHIBITED from:
 *   - Using this software for any purpose
 *   - Copying, reproducing, or duplicating this software
 *   - Modifying, adapting, or creating derivative works
 *   - Distributing, publishing, or transferring this software
 *   - Reverse engineering, decompiling, or disassembling this software
 *   - Sublicensing or permitting any third-party access
 *
 * LEGAL ENFORCEMENT:
 *
 * Unauthorized use will be prosecuted to the maximum extent of applicable law.
 *
 * For licensing inquiries: WeNova Interactive
 * =============================================================================
 */

/**
 * DNALockOS - DNA-Key Authentication System
 * Copyright (c) 2025 WeNova Interactive
 * Legal Owner: Kayden Shawn Massengill
 * ALL RIGHTS RESERVED.
 *
 * PROPRIETARY AND CONFIDENTIAL
 * This is commercial software. Unauthorized copying, modification,
 * distribution, or use is strictly prohibited.
 */

// Tron-Inspired Main Page
import React, { useState } from 'react';
import DNAVisualizer from '../components/DNAVisualizer';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [subjectId, setSubjectId] = useState('');
  const [keyData, setKeyData] = useState(null);
  const [visualConfig, setVisualConfig] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleEnroll = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v1/enroll`, {
        subject_id: subjectId,
        subject_type: 'human',
        security_level: 'enhanced',
        mfa_required: true
      });

      setKeyData(response.data);
      
      // Get visual DNA
      const visualResp = await axios.get(`${API_URL}/api/v1/visual/${response.data.key_id}`);
      setVisualConfig(visualResp.data);
    } catch (error) {
      console.error('Enrollment failed:', error);
      alert('Enrollment failed: ' + error.message);
    }
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <div style={styles.grid}>
        <div style={styles.header}>
          <h1 style={styles.title}>🔷 DNA-KEY AUTHENTICATION 🔷</h1>
          <p style={styles.subtitle}>Tron-Inspired Futuristic Security System</p>
        </div>

        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>ENROLL NEW KEY</h2>
          <input
            style={styles.input}
            type="text"
            placeholder="Enter Subject ID (email/username)"
            value={subjectId}
            onChange={(e) => setSubjectId(e.target.value)}
          />
          <button 
            style={styles.button}
            onClick={handleEnroll}
            disabled={loading || !subjectId}
          >
            {loading ? 'GENERATING DNA KEY...' : 'ENROLL →'}
          </button>
        </div>

        {keyData && (
          <div style={styles.resultPanel}>
            <h2 style={styles.panelTitle}>✓ KEY GENERATED</h2>
            <div style={styles.keyInfo}>
              <p><strong>KEY ID:</strong> {keyData.key_id}</p>
              <p><strong>CREATED:</strong> {new Date(keyData.created_at).toLocaleString()}</p>
              <p><strong>EXPIRES:</strong> {new Date(keyData.expires_at).toLocaleString()}</p>
              <p><strong>VISUAL SEED:</strong> {keyData.visual_seed}</p>
            </div>
          </div>
        )}

        {visualConfig && (
          <div style={styles.visualPanel}>
            <h2 style={styles.panelTitle}>3D DNA VISUALIZATION</h2>
            <DNAVisualizer keyId={keyData.key_id} visualConfig={visualConfig} />
          </div>
        )}
      </div>

      <div style={styles.footer}>
        <p>Powered by DNA-Key Authentication System v1.0</p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(180deg, #000000 0%, #0a0a1a 100%)',
    color: '#00ffff',
    fontFamily: '"Orbitron", "Courier New", monospace',
    padding: '20px'
  },
  grid: {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'grid',
    gap: '20px'
  },
  header: {
    textAlign: 'center',
    padding: '40px 0',
    borderBottom: '2px solid #00ffff',
    boxShadow: '0 0 20px rgba(0, 255, 255, 0.3)'
  },
  title: {
    fontSize: '48px',
    margin: 0,
    textShadow: '0 0 20px #00ffff',
    animation: 'glow 2s ease-in-out infinite'
  },
  subtitle: {
    fontSize: '18px',
    color: '#ff00ff',
    margin: '10px 0 0 0'
  },
  panel: {
    background: 'rgba(0, 255, 255, 0.05)',
    border: '2px solid #00ffff',
    borderRadius: '10px',
    padding: '30px',
    boxShadow: '0 0 30px rgba(0, 255, 255, 0.2)'
  },
  panelTitle: {
    fontSize: '24px',
    marginTop: 0,
    color: '#00ffff',
    textTransform: 'uppercase',
    letterSpacing: '3px'
  },
  input: {
    width: '100%',
    padding: '15px',
    fontSize: '16px',
    background: 'rgba(0, 0, 0, 0.5)',
    border: '2px solid #00ffff',
    borderRadius: '5px',
    color: '#00ffff',
    marginBottom: '20px',
    fontFamily: 'inherit'
  },
  button: {
    width: '100%',
    padding: '15px',
    fontSize: '18px',
    background: 'linear-gradient(90deg, #00ffff 0%, #00cccc 100%)',
    border: 'none',
    borderRadius: '5px',
    color: '#000',
    fontWeight: 'bold',
    cursor: 'pointer',
    textTransform: 'uppercase',
    letterSpacing: '2px',
    transition: 'all 0.3s',
    boxShadow: '0 0 20px rgba(0, 255, 255, 0.5)'
  },
  resultPanel: {
    background: 'rgba(0, 255, 0, 0.05)',
    border: '2px solid #00ff00',
    borderRadius: '10px',
    padding: '30px',
    boxShadow: '0 0 30px rgba(0, 255, 0, 0.2)'
  },
  keyInfo: {
    fontSize: '14px',
    lineHeight: '1.8'
  },
  visualPanel: {
    background: 'rgba(255, 0, 255, 0.05)',
    border: '2px solid #ff00ff',
    borderRadius: '10px',
    padding: '30px',
    boxShadow: '0 0 30px rgba(255, 0, 255, 0.2)'
  },
  footer: {
    textAlign: 'center',
    marginTop: '40px',
    padding: '20px',
    color: '#666',
    fontSize: '12px'
  }
};
