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

// 2D Fallback Viewer for devices without WebGL support
import React from 'react';

const DNAViewer2D = ({ visualConfig }) => {
  const { geometry } = visualConfig;
  
  // Create 2D representation
  const segments = geometry.points.slice(0, 100); // Show first 100 segments
  
  return (
    <div style={styles.container}>
      <h3 style={styles.title}>DNA Key Visualization (2D)</h3>
      <p style={styles.subtitle}>Your device doesn't support 3D, showing 2D representation</p>
      
      <div style={styles.helix}>
        {segments.map((point, i) => (
          <div 
            key={i}
            style={{
              ...styles.segment,
              backgroundColor: point.color,
              left: `${50 + Math.cos(i / 5) * 40}%`,
              top: `${(i / segments.length) * 90}%`
            }}
            title={`Segment ${i + 1}: ${point.type}`}
          />
        ))}
      </div>
      
      <div style={styles.legend}>
        <h4>Segment Types</h4>
        <div style={styles.legendGrid}>
          {[
            { type: 'E', color: '#00FFFF', name: 'Entropy' },
            { type: 'P', color: '#FF00FF', name: 'Policy' },
            { type: 'H', color: '#FFFF00', name: 'Hash' },
            { type: 'T', color: '#00FF00', name: 'Temporal' },
            { type: 'C', color: '#FF0000', name: 'Capability' }
          ].map(seg => (
            <div key={seg.type} style={styles.legendItem}>
              <span style={{...styles.legendDot, backgroundColor: seg.color}}></span>
              <span>{seg.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    width: '100%',
    minHeight: '600px',
    background: 'linear-gradient(135deg, #000 0%, #0a0a2e 100%)',
    borderRadius: '15px',
    border: '2px solid #00ffff',
    padding: '20px',
    color: '#00ffff'
  },
  title: {
    fontSize: '24px',
    textAlign: 'center',
    marginBottom: '10px',
    textShadow: '0 0 10px #00ffff'
  },
  subtitle: {
    fontSize: '14px',
    textAlign: 'center',
    color: '#888',
    marginBottom: '30px'
  },
  helix: {
    position: 'relative',
    width: '100%',
    height: '400px',
    background: 'rgba(0, 0, 0, 0.3)',
    borderRadius: '10px',
    overflow: 'hidden'
  },
  segment: {
    position: 'absolute',
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    boxShadow: '0 0 10px currentColor',
    animation: 'pulse 2s ease-in-out infinite'
  },
  legend: {
    marginTop: '20px'
  },
  legendGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '10px',
    marginTop: '10px'
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontSize: '14px'
  },
  legendDot: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    boxShadow: '0 0 5px currentColor'
  }
};

export default DNAViewer2D;
