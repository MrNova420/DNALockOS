"""
==============================================================================
DNALockOS - DNA-Key Authentication System
Copyright (c) 2025 WeNova Interactive
==============================================================================

OWNERSHIP AND LEGAL NOTICE:

This software and all associated intellectual property is the exclusive
property of WeNova Interactive, legally owned and operated by:

    Kayden Shawn Massengill

COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE

This is proprietary commercial software. It is NOT free software. It is NOT
open source software. This software is developed for commercial sale and
requires a valid commercial license for ANY use.

STRICT PROHIBITION NOTICE:

Without a valid commercial license agreement, you are PROHIBITED from:
  * Using this software for any purpose
  * Copying, reproducing, or duplicating this software
  * Modifying, adapting, or creating derivative works
  * Distributing, publishing, or transferring this software
  * Reverse engineering, decompiling, or disassembling this software
  * Sublicensing or permitting any third-party access

LEGAL ENFORCEMENT:

Unauthorized use, reproduction, or distribution of this software, or any
portion thereof, may result in severe civil and criminal penalties, and
will be prosecuted to the maximum extent possible under applicable law.

For licensing inquiries: WeNova Interactive
==============================================================================
"""

"""
DNALockOS - DNA-Key Authentication System
Copyright (c) 2025 WeNova Interactive
Legal Owner: Kayden Shawn Massengill
ALL RIGHTS RESERVED.

PROPRIETARY AND CONFIDENTIAL
This is commercial software. Unauthorized copying, modification,
distribution, or use is strictly prohibited.
"""

"""
DNA-Key Authentication System - Visual DNA Generator

Generates 3D visual DNA helix data for Three.js rendering.
Each DNA key gets a unique, deterministic visual representation.
"""

import math
from dataclasses import dataclass
from typing import Any, Dict

from server.crypto.dna_key import DNAKey, SegmentType

# Tron-inspired color scheme
SEGMENT_COLORS = {
    SegmentType.ENTROPY: "#00FFFF",  # Cyan
    SegmentType.POLICY: "#FF00FF",  # Magenta
    SegmentType.HASH: "#FFFF00",  # Yellow
    SegmentType.TEMPORAL: "#00FF00",  # Green
    SegmentType.CAPABILITY: "#FF0000",  # Red
    SegmentType.SIGNATURE: "#0000FF",  # Blue
    SegmentType.METADATA: "#FFA500",  # Orange
    SegmentType.BIOMETRIC: "#800080",  # Purple
    SegmentType.GEOLOCATION: "#00CED1",  # Turquoise
    SegmentType.REVOCATION: "#FF1493",  # Pink
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

            points.append({"x": x, "y": y, "z": z, "color": color, "type": segment.type.value, "glow": glow})

        return {
            "geometry": {"points": points, "radius": radius, "height": height, "turns": turns},
            "animation": {"rotation_speed": 0.01, "pulse_frequency": 2.0, "glow_intensity": 0.8},
            "particles": {"count": 1000, "flow": "spiral", "speed": 0.5},
            "seed": self.seed,
        }


def generate_visual_dna(dna_key: DNAKey) -> Dict[str, Any]:
    """Generate visual DNA config."""
    generator = VisualDNAGenerator(dna_key)
    return generator.generate()
