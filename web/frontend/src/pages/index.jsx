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

// Enhanced Main Page with Full 3D Viewer
import React, { useState } from 'react';
import FullDNAViewer from '../components/FullDNAViewer';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [activeTab, setActiveTab] = useState('enroll');
  const [subjectId, setSubjectId] = useState('');
  const [securityLevel, setSecurityLevel] = useState('enhanced');
  const [keyData, setKeyData] = useState(null);
  const [visualConfig, setVisualConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [authMode, setAuthMode] = useState(false);
  const [challengeData, setChallengeData] = useState(null);

  const mockVisualConfig = {
    geometry: {
      points: Array.from({ length: 1000 }, (_, i) => ({
        x: 100 * Math.cos(i / 100 * Math.PI * 2),
        y: i * 0.8,
        z: 100 * Math.sin(i / 100 * Math.PI * 2),
        color: ['#00FFFF', '#FF00FF', '#FFFF00', '#00FF00', '#FF0000'][i % 5],
        type: ['E', 'P', 'H', 'T', 'C'][i % 5],
        glow: 0.8 + Math.random() * 0.2
      })),
      radius: 100,
      height: 800,
      turns: 8
    },
    animation: {
      rotation_speed: 0.01,
      pulse_frequency: 2.0,
      glow_intensity: 0.8
    },
    particles: {
      count: 1000,
      flow: 'spiral',
      speed: 0.5
    }
  };

  const handleEnroll = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v1/enroll`, {
        subject_id: subjectId,
        subject_type: 'human',
        security_level: securityLevel,
        mfa_required: true,
        biometric_required: false,
        device_binding_required: true
      });

      setKeyData(response.data);
      setVisualConfig(mockVisualConfig); // Use mock data for demo
      setActiveTab('viewer');
    } catch (error) {
      console.error('Enrollment failed:', error);
      alert('Enrollment failed: ' + (error.response?.data?.error_message || error.message));
    }
    setLoading(false);
  };

  const handleAuthChallenge = async () => {
    if (!subjectId) {
      alert('Enter Key ID first');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/v1/challenge`, {
        key_id: subjectId
      });

      if (response.data.success) {
        setChallengeData(response.data);
        alert(`Challenge received! In production, you would sign this challenge with your DNA key.\n\nChallenge: ${response.data.challenge.substring(0, 32)}...`);
      }
    } catch (error) {
      alert('Challenge request failed: ' + error.message);
    }
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      {/* Animated Background */}
      <div style={styles.bgAnimation}>
        <div style={styles.grid}></div>
      </div>

      {/* Header */}
      <div style={styles.header}>
        <div style={styles.logo}>
          <span style={styles.logoIcon}>🔷</span>
          <h1 style={styles.logoText}>DNA-KEY</h1>
        </div>
        <div style={styles.tagline}>
          <span style={styles.taglineText}>AUTHENTICATION SYSTEM</span>
          <div style={styles.version}>v1.0 | DNA PROTOCOL</div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div style={styles.tabs}>
        <button 
          style={{...styles.tab, ...(activeTab === 'enroll' ? styles.activeTab : {})}}
          onClick={() => setActiveTab('enroll')}
        >
          ⚡ ENROLL
        </button>
        <button 
          style={{...styles.tab, ...(activeTab === 'authenticate' ? styles.activeTab : {})}}
          onClick={() => setActiveTab('authenticate')}
        >
          🔐 AUTHENTICATE
        </button>
        {visualConfig && (
          <button 
            style={{...styles.tab, ...(activeTab === 'viewer' ? styles.activeTab : {})}}
            onClick={() => setActiveTab('viewer')}
          >
            🌀 3D VIEWER
          </button>
        )}
        <button 
          style={{...styles.tab, ...(activeTab === 'demo' ? styles.activeTab : {})}}
          onClick={() => { setVisualConfig(mockVisualConfig); setActiveTab('demo'); }}
        >
          ✨ DEMO 3D
        </button>
      </div>

      {/* Content Area */}
      <div style={styles.content}>
        {activeTab === 'enroll' && (
          <div style={styles.panel}>
            <h2 style={styles.panelTitle}>🔷 ENROLL NEW DNA KEY 🔷</h2>
            <p style={styles.description}>
              Generate a unique DNA authentication key with thousands of cryptographic segments
            </p>

            <div style={styles.form}>
              <label style={styles.label}>SUBJECT ID</label>
              <input
                style={styles.input}
                type="text"
                placeholder="email@example.com or username"
                value={subjectId}
                onChange={(e) => setSubjectId(e.target.value)}
              />

              <label style={styles.label}>SECURITY LEVEL</label>
              <div style={styles.radioGroup}>
                {['standard', 'enhanced', 'maximum', 'government'].map(level => (
                  <label key={level} style={styles.radioLabel}>
                    <input
                      type="radio"
                      name="security"
                      value={level}
                      checked={securityLevel === level}
                      onChange={(e) => setSecurityLevel(e.target.value)}
                      style={styles.radio}
                    />
                    <span style={styles.radioText}>{level.toUpperCase()}</span>
                    <span style={styles.radioDesc}>
                      {level === 'standard' && '1,024 segments'}
                      {level === 'enhanced' && '16,384 segments'}
                      {level === 'maximum' && '65,536 segments'}
                      {level === 'government' && '262,144 segments'}
                    </span>
                  </label>
                ))}
              </div>

              <button 
                style={styles.primaryBtn}
                onClick={handleEnroll}
                disabled={loading || !subjectId}
              >
                {loading ? '⚡ GENERATING DNA KEY...' : '⚡ ENROLL NOW →'}
              </button>
            </div>

            {keyData && (
              <div style={styles.resultBox}>
                <h3 style={styles.resultTitle}>✓ DNA KEY GENERATED</h3>
                <div style={styles.keyDetails}>
                  <div style={styles.keyRow}>
                    <span style={styles.keyLabel}>KEY ID:</span>
                    <span style={styles.keyValue}>{keyData.key_id}</span>
                  </div>
                  <div style={styles.keyRow}>
                    <span style={styles.keyLabel}>CREATED:</span>
                    <span style={styles.keyValue}>{new Date(keyData.created_at).toLocaleString()}</span>
                  </div>
                  <div style={styles.keyRow}>
                    <span style={styles.keyLabel}>EXPIRES:</span>
                    <span style={styles.keyValue}>{new Date(keyData.expires_at).toLocaleString()}</span>
                  </div>
                  <div style={styles.keyRow}>
                    <span style={styles.keyLabel}>VISUAL SEED:</span>
                    <span style={styles.keyValue}>{keyData.visual_seed}</span>
                  </div>
                </div>
                <button 
                  style={styles.secondaryBtn}
                  onClick={() => setActiveTab('viewer')}
                >
                  🌀 VIEW IN 3D →
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'authenticate' && (
          <div style={styles.panel}>
            <h2 style={styles.panelTitle}>🔐 AUTHENTICATE WITH DNA KEY 🔐</h2>
            <p style={styles.description}>
              Challenge-response authentication using your DNA key signature
            </p>

            <div style={styles.form}>
              <label style={styles.label}>DNA KEY ID</label>
              <input
                style={styles.input}
                type="text"
                placeholder="dna-xxxxx..."
                value={subjectId}
                onChange={(e) => setSubjectId(e.target.value)}
              />

              <button 
                style={styles.primaryBtn}
                onClick={handleAuthChallenge}
                disabled={loading || !subjectId}
              >
                {loading ? '🔐 REQUESTING CHALLENGE...' : '🔐 GET CHALLENGE →'}
              </button>
            </div>

            {challengeData && (
              <div style={styles.resultBox}>
                <h3 style={styles.resultTitle}>✓ CHALLENGE RECEIVED</h3>
                <div style={styles.keyDetails}>
                  <div style={styles.keyRow}>
                    <span style={styles.keyLabel}>CHALLENGE ID:</span>
                    <span style={styles.keyValue}>{challengeData.challenge_id}</span>
                  </div>
                  <div style={styles.keyRow}>
                    <span style={styles.keyLabel}>CHALLENGE:</span>
                    <span style={styles.keyValue}>{challengeData.challenge.substring(0, 40)}...</span>
                  </div>
                  <div style={styles.keyRow}>
                    <span style={styles.keyLabel}>EXPIRES:</span>
                    <span style={styles.keyValue}>{new Date(challengeData.expires_at).toLocaleString()}</span>
                  </div>
                </div>
                <p style={styles.note}>
                  📝 In production, you would sign this challenge with your DNA key's private key
                  and submit the signature for authentication.
                </p>
              </div>
            )}
          </div>
        )}

        {(activeTab === 'viewer' || activeTab === 'demo') && visualConfig && (
          <div style={styles.viewerPanel}>
            <h2 style={styles.panelTitle}>🌀 3D DNA VISUALIZATION 🌀</h2>
            <p style={styles.description}>
              Full 360° interactive view of your unique DNA authentication key
            </p>
            <FullDNAViewer 
              keyId={keyData?.key_id || 'demo-key'} 
              visualConfig={visualConfig}
              onSegmentClick={(segment) => console.log('Segment clicked:', segment)}
            />
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={styles.footer}>
        <p>🔷 Powered by DNA-Key Authentication System v1.0 🔷</p>
        <p style={styles.footerLinks}>
          <a href="/admin" style={styles.link}>Admin Dashboard</a>
          {' | '}
          <a href="/api/docs" style={styles.link}>API Docs</a>
          {' | '}
          <a href="https://github.com" style={styles.link}>GitHub</a>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: '#000',
    color: '#00ffff',
    fontFamily: 'Orbitron, monospace',
    position: 'relative',
    overflow: 'hidden'
  },
  bgAnimation: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 0,
    opacity: 0.1
  },
  grid: {
    width: '100%',
    height: '100%',
    background: `
      linear-gradient(#00ffff 1px, transparent 1px),
      linear-gradient(90deg, #00ffff 1px, transparent 1px)
    `,
    backgroundSize: '50px 50px',
    animation: 'gridScroll 20s linear infinite'
  },
  header: {
    position: 'relative',
    zIndex: 1,
    textAlign: 'center',
    padding: '40px 20px 20px',
    borderBottom: '3px solid #00ffff',
    boxShadow: '0 0 30px rgba(0, 255, 255, 0.3)',
    background: 'linear-gradient(180deg, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0.4) 100%)',
    backdropFilter: 'blur(10px)'
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '20px'
  },
  logoIcon: {
    fontSize: '60px',
    animation: 'pulse 2s ease-in-out infinite'
  },
  logoText: {
    fontSize: '60px',
    fontWeight: '900',
    margin: 0,
    textShadow: '0 0 20px #00ffff, 0 0 40px #00ffff',
    letterSpacing: '5px'
  },
  tagline: {
    marginTop: '10px'
  },
  taglineText: {
    fontSize: '20px',
    color: '#ff00ff',
    letterSpacing: '8px',
    textShadow: '0 0 10px #ff00ff'
  },
  version: {
    fontSize: '12px',
    color: '#666',
    marginTop: '5px',
    letterSpacing: '2px'
  },
  tabs: {
    position: 'relative',
    zIndex: 1,
    display: 'flex',
    gap: '10px',
    padding: '20px',
    justifyContent: 'center',
    flexWrap: 'wrap'
  },
  tab: {
    padding: '15px 30px',
    background: 'rgba(0, 255, 255, 0.1)',
    border: '2px solid #00ffff',
    borderRadius: '10px',
    color: '#00ffff',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'all 0.3s',
    textTransform: 'uppercase',
    letterSpacing: '2px',
    fontFamily: 'Orbitron, monospace'
  },
  activeTab: {
    background: 'linear-gradient(90deg, #00ffff 0%, #00cccc 100%)',
    color: '#000',
    boxShadow: '0 0 30px rgba(0, 255, 255, 0.6)',
    transform: 'scale(1.05)'
  },
  content: {
    position: 'relative',
    zIndex: 1,
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '20px'
  },
  panel: {
    background: 'rgba(0, 0, 0, 0.8)',
    border: '3px solid #00ffff',
    borderRadius: '15px',
    padding: '40px',
    boxShadow: '0 0 50px rgba(0, 255, 255, 0.3), inset 0 0 30px rgba(0, 255, 255, 0.05)',
    backdropFilter: 'blur(10px)'
  },
  viewerPanel: {
    background: 'rgba(0, 0, 0, 0.9)',
    border: '3px solid #ff00ff',
    borderRadius: '15px',
    padding: '30px',
    boxShadow: '0 0 50px rgba(255, 0, 255, 0.3)',
    backdropFilter: 'blur(10px)'
  },
  panelTitle: {
    fontSize: '36px',
    textAlign: 'center',
    marginBottom: '15px',
    textShadow: '0 0 20px currentColor',
    letterSpacing: '3px'
  },
  description: {
    textAlign: 'center',
    fontSize: '16px',
    color: '#888',
    marginBottom: '40px',
    lineHeight: '1.6'
  },
  form: {
    maxWidth: '600px',
    margin: '0 auto'
  },
  label: {
    display: 'block',
    fontSize: '14px',
    fontWeight: 'bold',
    marginBottom: '10px',
    textTransform: 'uppercase',
    letterSpacing: '2px',
    color: '#00ffff'
  },
  input: {
    width: '100%',
    padding: '15px',
    fontSize: '16px',
    background: 'rgba(0, 0, 0, 0.5)',
    border: '2px solid #00ffff',
    borderRadius: '8px',
    color: '#00ffff',
    marginBottom: '25px',
    fontFamily: 'Orbitron, monospace',
    transition: 'all 0.3s'
  },
  radioGroup: {
    display: 'grid',
    gap: '15px',
    marginBottom: '30px'
  },
  radioLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '15px',
    background: 'rgba(0, 255, 255, 0.05)',
    border: '2px solid #00ffff',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s'
  },
  radio: {
    width: '20px',
    height: '20px',
    accentColor: '#00ffff'
  },
  radioText: {
    fontWeight: 'bold',
    fontSize: '14px',
    flex: '0 0 120px'
  },
  radioDesc: {
    fontSize: '12px',
    color: '#888'
  },
  primaryBtn: {
    width: '100%',
    padding: '20px',
    fontSize: '18px',
    fontWeight: 'bold',
    background: 'linear-gradient(90deg, #00ffff 0%, #00cccc 100%)',
    border: 'none',
    borderRadius: '10px',
    color: '#000',
    cursor: 'pointer',
    textTransform: 'uppercase',
    letterSpacing: '3px',
    transition: 'all 0.3s',
    boxShadow: '0 0 30px rgba(0, 255, 255, 0.5)',
    fontFamily: 'Orbitron, monospace'
  },
  secondaryBtn: {
    width: '100%',
    padding: '15px',
    fontSize: '16px',
    fontWeight: 'bold',
    background: 'rgba(255, 0, 255, 0.2)',
    border: '2px solid #ff00ff',
    borderRadius: '8px',
    color: '#ff00ff',
    cursor: 'pointer',
    textTransform: 'uppercase',
    letterSpacing: '2px',
    transition: 'all 0.3s',
    fontFamily: 'Orbitron, monospace'
  },
  resultBox: {
    marginTop: '40px',
    padding: '30px',
    background: 'rgba(0, 255, 0, 0.05)',
    border: '2px solid #00ff00',
    borderRadius: '10px',
    boxShadow: '0 0 20px rgba(0, 255, 0, 0.2)'
  },
  resultTitle: {
    fontSize: '24px',
    color: '#00ff00',
    marginBottom: '20px',
    textAlign: 'center',
    textShadow: '0 0 15px #00ff00'
  },
  keyDetails: {
    marginBottom: '20px'
  },
  keyRow: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px 0',
    borderBottom: '1px solid rgba(0, 255, 255, 0.2)',
    fontSize: '14px'
  },
  keyLabel: {
    fontWeight: 'bold',
    color: '#888'
  },
  keyValue: {
    color: '#00ffff',
    wordBreak: 'break-all'
  },
  note: {
    fontSize: '14px',
    color: '#ffff00',
    padding: '15px',
    background: 'rgba(255, 255, 0, 0.1)',
    border: '1px solid #ffff00',
    borderRadius: '5px',
    marginTop: '20px'
  },
  footer: {
    position: 'relative',
    zIndex: 1,
    textAlign: 'center',
    padding: '40px 20px',
    marginTop: '60px',
    borderTop: '2px solid #00ffff',
    background: 'rgba(0, 0, 0, 0.8)',
    fontSize: '14px',
    color: '#666'
  },
  footerLinks: {
    marginTop: '10px'
  },
  link: {
    color: '#00ffff',
    textDecoration: 'none',
    transition: 'all 0.3s'
  }
};
