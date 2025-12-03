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

// Enhanced 3D DNA Viewer - Full 360° Interactive Experience
import React, { useRef, useState, useEffect, Suspense } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { 
  OrbitControls, 
  PerspectiveCamera,
  Sparkles,
  Float
} from '@react-three/drei';
import * as THREE from 'three';

// DNA Helix with full 360° rotation and interaction
const InteractiveDNAHelix = ({ visualConfig }) => {
  const groupRef = useRef();
  const { geometry, animation } = visualConfig;
  const [hoveredPoint, setHoveredPoint] = useState(null);
  
  // Create helix geometry
  const helixGeometry = React.useMemo(() => {
    const positions = new Float32Array(geometry.points.length * 3);
    const colors = new Float32Array(geometry.points.length * 3);
    const sizes = new Float32Array(geometry.points.length);

    geometry.points.forEach((p, i) => {
      positions[i * 3] = p.x;
      positions[i * 3 + 1] = p.y;
      positions[i * 3 + 2] = p.z;
      
      const color = new THREE.Color(p.color);
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
      
      sizes[i] = 4 + Math.random() * 2;
    });

    return { positions, colors, sizes };
  }, [geometry.points]);

  // Animate helix
  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = clock.getElapsedTime() * animation.rotation_speed * 2;
      
      // Pulse effect
      const scale = 1 + Math.sin(clock.getElapsedTime() * animation.pulse_frequency) * 0.15;
      groupRef.current.scale.set(scale, 1, scale);
    }
  });

  return (
    <group ref={groupRef}>
      {/* Main DNA points with glow */}
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
          <bufferAttribute
            attach="attributes-size"
            count={helixGeometry.sizes.length}
            array={helixGeometry.sizes}
            itemSize={1}
          />
        </bufferGeometry>
        <pointsMaterial
          size={3}
          vertexColors
          transparent
          opacity={0.9}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>

      {/* Connecting lines between strands */}
      <DNAConnectors points={geometry.points} />
      
      {/* Particle system flowing through helix */}
      <Sparkles 
        count={1000} 
        scale={[geometry.radius * 3, geometry.height, geometry.radius * 3]}
        size={2}
        speed={0.5}
        opacity={0.6}
        color="#00ffff"
      />
    </group>
  );
};

// DNA connector lines
const DNAConnectors = ({ points }) => {
  const lineRef = useRef();
  
  useFrame(({ clock }) => {
    if (lineRef.current) {
      lineRef.current.material.opacity = 0.3 + Math.sin(clock.getElapsedTime() * 2) * 0.2;
    }
  });

  const linePositions = React.useMemo(() => {
    const positions = [];
    // Connect opposite points in the helix
    for (let i = 0; i < points.length - 1; i += 2) {
      const p1 = points[i];
      const p2 = points[i + 1];
      if (p1 && p2) {
        positions.push(p1.x, p1.y, p1.z);
        positions.push(p2.x, p2.y, p2.z);
      }
    }
    return new Float32Array(positions);
  }, [points]);

  return (
    <lineSegments ref={lineRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={linePositions.length / 3}
          array={linePositions}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial 
        color="#00ffff" 
        transparent 
        opacity={0.3}
        blending={THREE.AdditiveBlending}
      />
    </lineSegments>
  );
};

// Floating particle rings around DNA
const ParticleRings = () => {
  return (
    <>
      {[0, 1, 2].map((i) => (
        <Float
          key={i}
          speed={2 + i}
          rotationIntensity={0.5}
          floatIntensity={0.5}
        >
          <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 300 + i * 300, 0]}>
            <torusGeometry args={[150 + i * 50, 2, 16, 100]} />
            <meshBasicMaterial 
              color={i === 0 ? "#00ffff" : i === 1 ? "#ff00ff" : "#ffff00"}
              transparent 
              opacity={0.3}
              blending={THREE.AdditiveBlending}
            />
          </mesh>
        </Float>
      ))}
    </>
  );
};

// Main 3D DNA Viewer Component
const FullDNAViewer = ({ keyId, visualConfig, onSegmentClick }) => {
  const [controlsEnabled, setControlsEnabled] = useState(true);
  const [autoRotate, setAutoRotate] = useState(true);
  const [showParticles, setShowParticles] = useState(true);
  const [showGrid, setShowGrid] = useState(false);
  const [viewMode, setViewMode] = useState('full'); // full, top, side

  return (
    <div style={styles.viewerContainer}>
      {/* Control Panel */}
      <div style={styles.controls}>
        <div style={styles.controlGroup}>
          <h3 style={styles.controlTitle}>🎮 VIEWER CONTROLS</h3>
          <button 
            style={styles.controlBtn}
            onClick={() => setAutoRotate(!autoRotate)}
          >
            {autoRotate ? '⏸ PAUSE ROTATION' : '▶ AUTO ROTATE'}
          </button>
          <button 
            style={styles.controlBtn}
            onClick={() => setShowParticles(!showParticles)}
          >
            {showParticles ? '✨ HIDE PARTICLES' : '✨ SHOW PARTICLES'}
          </button>
          <button 
            style={styles.controlBtn}
            onClick={() => setShowGrid(!showGrid)}
          >
            {showGrid ? '📐 HIDE GRID' : '📐 SHOW GRID'}
          </button>
        </div>

        <div style={styles.controlGroup}>
          <h3 style={styles.controlTitle}>📐 VIEW MODE</h3>
          <button 
            style={{...styles.controlBtn, ...(viewMode === 'full' ? styles.activeBtn : {})}}
            onClick={() => setViewMode('full')}
          >
            360° VIEW
          </button>
          <button 
            style={{...styles.controlBtn, ...(viewMode === 'top' ? styles.activeBtn : {})}}
            onClick={() => setViewMode('top')}
          >
            TOP VIEW
          </button>
          <button 
            style={{...styles.controlBtn, ...(viewMode === 'side' ? styles.activeBtn : {})}}
            onClick={() => setViewMode('side')}
          >
            SIDE VIEW
          </button>
        </div>

        <div style={styles.info}>
          <h3 style={styles.controlTitle}>ℹ DNA INFO</h3>
          <p><strong>KEY ID:</strong> {keyId}</p>
          <p><strong>SEGMENTS:</strong> {visualConfig.geometry.points.length}</p>
          <p><strong>HEIGHT:</strong> {visualConfig.geometry.height}px</p>
          <p><strong>RADIUS:</strong> {visualConfig.geometry.radius}px</p>
          <p><strong>TURNS:</strong> {visualConfig.geometry.turns}</p>
        </div>

        <div style={styles.legend}>
          <h3 style={styles.controlTitle}>🎨 SEGMENT TYPES</h3>
          <div style={styles.legendItem}><span style={{color: '#00FFFF'}}>●</span> ENTROPY</div>
          <div style={styles.legendItem}><span style={{color: '#FF00FF'}}>●</span> POLICY</div>
          <div style={styles.legendItem}><span style={{color: '#FFFF00'}}>●</span> HASH</div>
          <div style={styles.legendItem}><span style={{color: '#00FF00'}}>●</span> TEMPORAL</div>
          <div style={styles.legendItem}><span style={{color: '#FF0000'}}>●</span> CAPABILITY</div>
          <div style={styles.legendItem}><span style={{color: '#0000FF'}}>●</span> SIGNATURE</div>
          <div style={styles.legendItem}><span style={{color: '#FFA500'}}>●</span> METADATA</div>
          <div style={styles.legendItem}><span style={{color: '#800080'}}>●</span> BIOMETRIC</div>
          <div style={styles.legendItem}><span style={{color: '#00CED1'}}>●</span> GEOLOCATION</div>
          <div style={styles.legendItem}><span style={{color: '#FF1493'}}>●</span> REVOCATION</div>
        </div>
      </div>

      {/* 3D Canvas */}
      <div style={styles.canvas}>
        <Canvas
          camera={{ position: [0, 500, 800], fov: 60 }}
          gl={{ 
            antialias: true, 
            alpha: true,
            powerPreference: "high-performance"
          }}
        >
          {/* Lighting */}
          <ambientLight intensity={0.3} />
          <pointLight position={[200, 300, 200]} intensity={1} color="#00ffff" />
          <pointLight position={[-200, 300, -200]} intensity={0.8} color="#ff00ff" />
          <spotLight 
            position={[0, 1000, 0]} 
            angle={0.3} 
            penumbra={1} 
            intensity={1}
            color="#00ffff"
            castShadow
          />

          {/* Camera Controls - Full 360° rotation */}
          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={controlsEnabled}
            autoRotate={autoRotate}
            autoRotateSpeed={1}
            minDistance={300}
            maxDistance={2000}
            maxPolarAngle={Math.PI}
            minPolarAngle={0}
          />

          {/* Main DNA Helix */}
          <Suspense fallback={null}>
            <InteractiveDNAHelix visualConfig={visualConfig} />
          </Suspense>

          {/* Particle Rings */}
          {showParticles && <ParticleRings />}

          {/* Grid Helper */}
          {showGrid && (
            <>
              <gridHelper args={[2000, 40, '#00ffff', '#003333']} />
              <axesHelper args={[500]} />
            </>
          )}

          {/* Environment - disabled for compatibility (requires external HDR files) */}
          
          {/* Post-processing effects - disabled for compatibility */}
          {/* Note: Bloom and other effects require @react-three/postprocessing package */}
        </Canvas>

        {/* Overlay instructions */}
        <div style={styles.instructions}>
          <p>🖱 <strong>LEFT CLICK + DRAG:</strong> Rotate 360°</p>
          <p>🖱 <strong>RIGHT CLICK + DRAG:</strong> Pan</p>
          <p>🖱 <strong>SCROLL:</strong> Zoom In/Out</p>
          <p>⌨️ <strong>KEYBOARD:</strong> Arrow keys to rotate</p>
        </div>
      </div>
    </div>
  );
};

const styles = {
  viewerContainer: {
    display: 'flex',
    gap: '20px',
    minHeight: '800px',
    background: 'linear-gradient(135deg, #000000 0%, #0a0a2e 100%)',
    borderRadius: '15px',
    border: '3px solid #00ffff',
    padding: '20px',
    boxShadow: '0 0 50px rgba(0, 255, 255, 0.4), inset 0 0 50px rgba(0, 255, 255, 0.1)',
    position: 'relative',
    overflow: 'hidden'
  },
  controls: {
    width: '300px',
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    overflowY: 'auto',
    paddingRight: '10px'
  },
  controlGroup: {
    background: 'rgba(0, 255, 255, 0.05)',
    border: '2px solid #00ffff',
    borderRadius: '10px',
    padding: '15px'
  },
  controlTitle: {
    fontSize: '16px',
    marginBottom: '10px',
    color: '#00ffff',
    textTransform: 'uppercase',
    letterSpacing: '2px',
    textShadow: '0 0 10px #00ffff'
  },
  controlBtn: {
    width: '100%',
    padding: '12px',
    margin: '5px 0',
    background: 'linear-gradient(90deg, rgba(0, 255, 255, 0.2) 0%, rgba(0, 255, 255, 0.1) 100%)',
    border: '2px solid #00ffff',
    borderRadius: '5px',
    color: '#00ffff',
    fontSize: '14px',
    fontWeight: 'bold',
    cursor: 'pointer',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    transition: 'all 0.3s',
    fontFamily: 'Orbitron, monospace'
  },
  activeBtn: {
    background: 'linear-gradient(90deg, #00ffff 0%, #00cccc 100%)',
    color: '#000',
    boxShadow: '0 0 20px rgba(0, 255, 255, 0.6)'
  },
  info: {
    background: 'rgba(255, 0, 255, 0.05)',
    border: '2px solid #ff00ff',
    borderRadius: '10px',
    padding: '15px',
    fontSize: '13px',
    lineHeight: '1.8'
  },
  legend: {
    background: 'rgba(255, 255, 0, 0.05)',
    border: '2px solid #ffff00',
    borderRadius: '10px',
    padding: '15px'
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontSize: '12px',
    margin: '5px 0',
    letterSpacing: '1px'
  },
  canvas: {
    flex: 1,
    position: 'relative',
    borderRadius: '10px',
    overflow: 'hidden',
    background: 'radial-gradient(circle at center, #0a0a2e 0%, #000000 100%)'
  },
  instructions: {
    position: 'absolute',
    bottom: '20px',
    left: '20px',
    background: 'rgba(0, 0, 0, 0.8)',
    border: '2px solid #00ffff',
    borderRadius: '10px',
    padding: '15px',
    fontSize: '12px',
    color: '#00ffff',
    backdropFilter: 'blur(10px)'
  }
};

export default FullDNAViewer;
