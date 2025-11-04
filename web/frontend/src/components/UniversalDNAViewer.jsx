// Universal 3D DNA Viewer - Optimized for ALL Devices
// Works on desktop, mobile, tablets, low-end devices, everything!

import React, { useRef, useState, useEffect, useMemo, Suspense } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { 
  OrbitControls, 
  PerspectiveCamera,
  Environment,
  AdaptiveDpr,
  AdaptiveEvents,
  useDetectGPU
} from '@react-three/drei';
import * as THREE from 'three';

// Device detection
const detectDevice = () => {
  if (typeof window === 'undefined') return 'desktop';
  
  const ua = navigator.userAgent.toLowerCase();
  const isMobile = /mobile|android|ios|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua);
  const isTablet = /tablet|ipad/i.test(ua);
  const isLowEnd = navigator.hardwareConcurrency <= 2 || !navigator.gpu;
  
  return {
    isMobile,
    isTablet,
    isLowEnd,
    isTouch: 'ontouchstart' in window,
    pixelRatio: Math.min(window.devicePixelRatio || 1, 2)
  };
};

// Adaptive settings based on device
const getDeviceSettings = (device) => {
  if (device.isMobile) {
    return {
      particles: 200,
      segments: 500,
      quality: 'low',
      shadows: false,
      antialiasing: false,
      pixelRatio: 1
    };
  }
  
  if (device.isTablet) {
    return {
      particles: 500,
      segments: 1000,
      quality: 'medium',
      shadows: false,
      antialiasing: true,
      pixelRatio: 1.5
    };
  }
  
  if (device.isLowEnd) {
    return {
      particles: 300,
      segments: 800,
      quality: 'low',
      shadows: false,
      antialiasing: false,
      pixelRatio: 1
    };
  }
  
  return {
    particles: 1000,
    segments: 2000,
    quality: 'high',
    shadows: true,
    antialiasing: true,
    pixelRatio: 2
  };
};

// Simplified DNA Helix for mobile/low-end devices
const SimpleDNAHelix = ({ visualConfig, settings }) => {
  const groupRef = useRef();
  const { geometry, animation } = visualConfig;
  
  // Reduce points based on device
  const pointsToRender = Math.min(geometry.points.length, settings.segments);
  
  const helixGeometry = useMemo(() => {
    const positions = new Float32Array(pointsToRender * 3);
    const colors = new Float32Array(pointsToRender * 3);
    
    const step = Math.floor(geometry.points.length / pointsToRender);
    
    for (let i = 0; i < pointsToRender; i++) {
      const point = geometry.points[i * step] || geometry.points[0];
      
      positions[i * 3] = point.x;
      positions[i * 3 + 1] = point.y;
      positions[i * 3 + 2] = point.z;
      
      const color = new THREE.Color(point.color);
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }
    
    return { positions, colors };
  }, [geometry.points, pointsToRender]);
  
  // Simple animation
  useFrame(({ clock }) => {
    if (groupRef.current && animation) {
      groupRef.current.rotation.y = clock.getElapsedTime() * (animation.rotation_speed || 0.01);
    }
  });
  
  return (
    <group ref={groupRef}>
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={helixGeometry.positions.length / 3}
            array={helixGeometry.positions}
            itemSize={3}
          />
          <bufferAttribute
            attach="attributes-color"
            count={helixGeometry.colors.length / 3}
            array={helixGeometry.colors}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          size={settings.quality === 'high' ? 3 : 2}
          vertexColors
          transparent
          opacity={0.9}
          sizeAttenuation
        />
      </points>
    </group>
  );
};

// Touch-friendly controls wrapper
const TouchControls = ({ children, enabled }) => {
  const { camera, gl } = useThree();
  
  useEffect(() => {
    if (!enabled) return;
    
    const handleTouchStart = (e) => {
      e.preventDefault();
    };
    
    gl.domElement.addEventListener('touchstart', handleTouchStart, { passive: false });
    
    return () => {
      gl.domElement.removeEventListener('touchstart', handleTouchStart);
    };
  }, [gl, enabled]);
  
  return children;
};

// Loading fallback
const LoadingFallback = () => (
  <div style={styles.loading}>
    <div style={styles.spinner}></div>
    <p style={styles.loadingText}>Loading 3D DNA Viewer...</p>
  </div>
);

// Universal 3D DNA Viewer Component
const UniversalDNAViewer = ({ keyId, visualConfig, onSegmentClick }) => {
  const [device, setDevice] = useState(null);
  const [settings, setSettings] = useState(null);
  const [autoRotate, setAutoRotate] = useState(true);
  const [quality, setQuality] = useState('auto');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Detect device on mount
  useEffect(() => {
    try {
      const detectedDevice = detectDevice();
      setDevice(detectedDevice);
      
      const deviceSettings = getDeviceSettings(detectedDevice);
      setSettings(deviceSettings);
      
      setIsLoading(false);
    } catch (err) {
      setError('Failed to initialize 3D viewer');
      setIsLoading(false);
    }
  }, []);
  
  // Handle quality change
  const handleQualityChange = (newQuality) => {
    setQuality(newQuality);
    
    const qualitySettings = {
      low: { particles: 200, segments: 500, pixelRatio: 1 },
      medium: { particles: 500, segments: 1000, pixelRatio: 1.5 },
      high: { particles: 1000, segments: 2000, pixelRatio: 2 },
      auto: settings
    };
    
    setSettings({ ...settings, ...qualitySettings[newQuality] });
  };
  
  if (isLoading) {
    return <LoadingFallback />;
  }
  
  if (error) {
    return (
      <div style={styles.error}>
        <h3>❌ {error}</h3>
        <p>Your device may not support WebGL.</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }
  
  return (
    <div style={styles.container}>
      {/* Mobile-friendly controls */}
      <div style={styles.mobileControls}>
        <div style={styles.controlGroup}>
          <button 
            style={styles.controlBtn}
            onClick={() => setAutoRotate(!autoRotate)}
          >
            {autoRotate ? '⏸' : '▶'} Rotate
          </button>
          
          <select 
            style={styles.controlBtn}
            value={quality}
            onChange={(e) => handleQualityChange(e.target.value)}
          >
            <option value="auto">Auto</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        
        {device.isMobile && (
          <div style={styles.touchHint}>
            👆 Drag to rotate • Pinch to zoom
          </div>
        )}
      </div>
      
      {/* 3D Canvas */}
      <div style={styles.canvas}>
        <Canvas
          dpr={settings.pixelRatio}
          camera={{ position: [0, 500, 800], fov: 60 }}
          gl={{ 
            antialias: settings.antialiasing,
            alpha: true,
            powerPreference: device.isLowEnd ? "low-power" : "high-performance"
          }}
          style={{ touchAction: 'none' }}
        >
          {/* Adaptive quality */}
          <AdaptiveDpr pixelated />
          <AdaptiveEvents />
          
          {/* Lighting */}
          <ambientLight intensity={0.5} />
          <pointLight position={[100, 200, 100]} intensity={1} color="#00ffff" />
          
          {/* Touch-friendly controls */}
          <OrbitControls
            enablePan={!device.isMobile}
            enableZoom={true}
            enableRotate={true}
            autoRotate={autoRotate}
            autoRotateSpeed={device.isMobile ? 0.5 : 1}
            minDistance={200}
            maxDistance={1500}
            touches={{
              ONE: THREE.TOUCH.ROTATE,
              TWO: THREE.TOUCH.DOLLY_PAN
            }}
          />
          
          {/* DNA Helix */}
          <Suspense fallback={null}>
            <SimpleDNAHelix 
              visualConfig={visualConfig} 
              settings={settings}
            />
          </Suspense>
        </Canvas>
      </div>
      
      {/* Info overlay */}
      <div style={styles.info}>
        <div style={styles.infoItem}>
          <strong>Device:</strong> {device.isMobile ? '📱 Mobile' : device.isTablet ? '📱 Tablet' : '💻 Desktop'}
        </div>
        <div style={styles.infoItem}>
          <strong>Quality:</strong> {quality === 'auto' ? settings.quality : quality}
        </div>
        <div style={styles.infoItem}>
          <strong>Segments:</strong> {settings.segments}/{visualConfig.geometry.points.length}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    position: 'relative',
    width: '100%',
    height: '600px',
    background: 'linear-gradient(135deg, #000 0%, #0a0a2e 100%)',
    borderRadius: '15px',
    overflow: 'hidden',
    border: '2px solid #00ffff',
    boxShadow: '0 0 30px rgba(0, 255, 255, 0.3)'
  },
  mobileControls: {
    position: 'absolute',
    top: '10px',
    left: '10px',
    right: '10px',
    zIndex: 10,
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  controlGroup: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap'
  },
  controlBtn: {
    padding: '10px 15px',
    background: 'rgba(0, 255, 255, 0.2)',
    border: '2px solid #00ffff',
    borderRadius: '5px',
    color: '#00ffff',
    fontSize: '14px',
    fontWeight: 'bold',
    cursor: 'pointer',
    fontFamily: 'Orbitron, monospace',
    WebkitTapHighlightColor: 'transparent'
  },
  touchHint: {
    padding: '8px',
    background: 'rgba(0, 255, 255, 0.1)',
    border: '1px solid #00ffff',
    borderRadius: '5px',
    color: '#00ffff',
    fontSize: '12px',
    textAlign: 'center'
  },
  canvas: {
    width: '100%',
    height: '100%',
    touchAction: 'none'
  },
  info: {
    position: 'absolute',
    bottom: '10px',
    left: '10px',
    padding: '10px',
    background: 'rgba(0, 0, 0, 0.8)',
    border: '1px solid #00ffff',
    borderRadius: '5px',
    color: '#00ffff',
    fontSize: '11px',
    backdropFilter: 'blur(10px)'
  },
  infoItem: {
    marginBottom: '5px'
  },
  loading: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '600px',
    background: 'linear-gradient(135deg, #000 0%, #0a0a2e 100%)',
    border: '2px solid #00ffff',
    borderRadius: '15px'
  },
  spinner: {
    width: '50px',
    height: '50px',
    border: '4px solid rgba(0, 255, 255, 0.3)',
    borderTop: '4px solid #00ffff',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  },
  loadingText: {
    marginTop: '20px',
    color: '#00ffff',
    fontSize: '16px'
  },
  error: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '600px',
    background: 'linear-gradient(135deg, #000 0%, #2e0a0a 100%)',
    border: '2px solid #ff0000',
    borderRadius: '15px',
    color: '#ff0000',
    padding: '20px',
    textAlign: 'center'
  }
};

// Add spinner animation
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `;
  document.head.appendChild(style);
}

export default UniversalDNAViewer;
