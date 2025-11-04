"""
DNA-Key Authentication System - Visual DNA Generator

Generates 3D visual DNA helix data for Three.js rendering.
Each DNA key gets a unique, deterministic visual representation.
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import math
import hashlib

from server.crypto.dna_key import DNAKey, SegmentType

# Tron-inspired color scheme
SEGMENT_COLORS = {
    SegmentType.ENTROPY: "#00FFFF",      # Cyan
    SegmentType.POLICY: "#FF00FF",       # Magenta
    SegmentType.HASH: "#FFFF00",         # Yellow  
    SegmentType.TEMPORAL: "#00FF00",     # Green
    SegmentType.CAPABILITY: "#FF0000",   # Red
    SegmentType.SIGNATURE: "#0000FF",    # Blue
    SegmentType.METADATA: "#FFA500",     # Orange
    SegmentType.BIOMETRIC: "#800080",    # Purple
    SegmentType.GEOLOCATION: "#00CED1",  # Turquoise
    SegmentType.REVOCATION: "#FF1493"    # Pink
}

@dataclass
class HelixPoint:
    """3D point on DNA helix."""
    x: float
    y: float
    z: float
    color: str
    segment_type: str
    glow: float

class VisualDNAGenerator:
    """Generate 3D visual DNA configuration."""
    
    def __init__(self, dna_key: DNAKey):
        self.dna_key = dna_key
        self.seed = dna_key.visual_dna.animation_seed if dna_key.visual_dna else dna_key.key_id
    
    def generate(self, radius: float = 100, height: float = 1000, turns: int = 10) -> Dict[str, Any]:
        """Generate complete visual configuration."""
        points = []
        segments = self.dna_key.dna_helix.segments
        num_points = min(len(segments), 5000)
        step = len(segments) / num_points if num_points > 0 else 1
        
        for i in range(num_points):
            t = i / num_points
            angle = t * turns * 2 * math.pi
            
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            y = t * height
            
            seg_idx = int(i * step) % len(segments)
            segment = segments[seg_idx]
            color = SEGMENT_COLORS.get(segment.type, "#FFFFFF")
            glow = 0.8 + (segment.data[0] / 255.0 * 0.2) if len(segment.data) > 0 else 0.8
            
            points.append({
                "x": x, "y": y, "z": z,
                "color": color,
                "type": segment.type.value,
                "glow": glow
            })
        
        return {
            "geometry": {
                "points": points,
                "radius": radius,
                "height": height,
                "turns": turns
            },
            "animation": {
                "rotation_speed": 0.01,
                "pulse_frequency": 2.0,
                "glow_intensity": 0.8
            },
            "particles": {
                "count": 1000,
                "flow": "spiral",
                "speed": 0.5
            },
            "seed": self.seed
        }

def generate_visual_dna(dna_key: DNAKey) -> Dict[str, Any]:
    """Generate visual DNA config."""
    generator = VisualDNAGenerator(dna_key)
    return generator.generate()
