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
