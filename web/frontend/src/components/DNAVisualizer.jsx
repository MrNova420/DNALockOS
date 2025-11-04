// DNA Helix 3D Visualizer Component (React + Three.js)
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

const DNAHelix = ({ visualConfig }) => {
  const pointsRef = useRef();
  const { geometry, animation } = visualConfig;

  // Create geometry from points
  const positions = useMemo(() => {
    const pos = new Float32Array(geometry.points.length * 3);
    geometry.points.forEach((p, i) => {
      pos[i * 3] = p.x;
      pos[i * 3 + 1] = p.y;
      pos[i * 3 + 2] = p.z;
    });
    return pos;
  }, [geometry.points]);

  const colors = useMemo(() => {
    const cols = new Float32Array(geometry.points.length * 3);
    geometry.points.forEach((p, i) => {
      const color = new THREE.Color(p.color);
      cols[i * 3] = color.r;
      cols[i * 3 + 1] = color.g;
      cols[i * 3 + 2] = color.b;
    });
    return cols;
  }, [geometry.points]);

  // Animation
  useFrame(({ clock }) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = clock.getElapsedTime() * animation.rotation_speed;
      
      // Pulse effect
      const scale = 1 + Math.sin(clock.getElapsedTime() * animation.pulse_frequency) * 0.1;
      pointsRef.current.scale.set(scale, 1, scale);
    }
  });

  return (
    <Points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={colors.length / 3}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <PointMaterial
        size={3}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
};

const DNAVisualizer = ({ keyId, visualConfig }) => {
  return (
    <div style={{ width: '100%', height: '600px', background: '#0a0a0a' }}>
      <Canvas camera={{ position: [0, 500, 800], fov: 75 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[100, 100, 100]} intensity={1} color="#00ffff" />
        <DNAHelix visualConfig={visualConfig} />
      </Canvas>
    </div>
  );
};

export default DNAVisualizer;
