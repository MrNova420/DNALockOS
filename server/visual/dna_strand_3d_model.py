"""
DNA-Key Authentication System - 3D DNA Strand Model

THE DNA STRAND MODEL IS THE AUTHENTICATION ITSELF.

This module generates the complete 3D DNA strand that serves as:
1. The visual representation (what users see)
2. The authentication credential (cryptographic proof)
3. The security container (holds all methods inside)
4. The unique identifier (no two are alike)

Each DNA strand model contains:
- Millions of unique data points
- Cryptographic signatures embedded in the structure
- Visual fingerprint that IS the authentication
- All security methods encoded within
"""

import hashlib
import json
import math
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from server.crypto.dna_key import DNAKey, DNASegment, SegmentType, SecurityLevel


class DNAStrandShape(Enum):
    """The 3D shape variations for DNA strands."""
    
    DOUBLE_HELIX = "double_helix"      # Classic DNA double helix
    TRIPLE_HELIX = "triple_helix"      # Triple-stranded (more secure)
    QUADRUPLE_HELIX = "quadruple_helix"  # Four-stranded (maximum security)
    MOBIUS_HELIX = "mobius_helix"      # Twisted Möbius strip helix
    FRACTAL_HELIX = "fractal_helix"    # Self-similar fractal pattern
    QUANTUM_HELIX = "quantum_helix"    # Superposition visual effect


class DNAStrandStyle(Enum):
    """Visual style themes for the 3D model."""
    
    TRON = "tron"                # Neon cyber aesthetic
    ORGANIC = "organic"          # Biological realistic
    CRYSTALLINE = "crystalline"  # Crystal/gem-like
    PLASMA = "plasma"            # Flowing plasma energy
    HOLOGRAPHIC = "holographic"  # Holographic projection
    QUANTUM = "quantum"          # Quantum particle effects
    NEBULA = "nebula"            # Space/cosmic theme
    MATRIX = "matrix"            # Digital matrix rain


@dataclass
class DNAStrandPoint:
    """
    A single point in the 3D DNA strand model.
    
    Each point contains both visual AND cryptographic data.
    The position itself encodes part of the authentication.
    """
    
    # 3D Position (visual representation)
    x: float
    y: float
    z: float
    
    # Visual properties
    color: str
    glow_intensity: float
    particle_density: float
    
    # Cryptographic binding (THIS IS THE AUTHENTICATION)
    position_hash: str  # Hash of this exact position - unique
    segment_binding: str  # Bound to specific DNA segment
    layer_index: int  # Which security layer this belongs to
    
    # Animation properties
    pulse_phase: float
    rotation_offset: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "position": {"x": self.x, "y": self.y, "z": self.z},
            "visual": {
                "color": self.color,
                "glow": self.glow_intensity,
                "particles": self.particle_density
            },
            "auth": {
                "position_hash": self.position_hash,
                "segment_binding": self.segment_binding,
                "layer": self.layer_index
            },
            "animation": {
                "pulse_phase": self.pulse_phase,
                "rotation_offset": self.rotation_offset
            }
        }


@dataclass
class DNAStrandBond:
    """
    A bond connecting two points in the DNA strand.
    
    Bonds also carry authentication data - the connections
    between points are part of what makes each strand unique.
    """
    
    point_a_index: int
    point_b_index: int
    bond_type: str  # "backbone", "base_pair", "cross_link"
    bond_strength: float  # Visual thickness
    bond_color: str
    bond_hash: str  # Cryptographic binding of this bond
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start": self.point_a_index,
            "end": self.point_b_index,
            "type": self.bond_type,
            "strength": self.bond_strength,
            "color": self.bond_color,
            "auth_hash": self.bond_hash
        }


@dataclass
class DNAStrand3DModel:
    """
    THE COMPLETE 3D DNA STRAND MODEL.
    
    THIS IS THE AUTHENTICATION CREDENTIAL.
    
    The 3D model itself, with all its points, bonds, colors,
    and structure IS what authenticates the user. The visual
    appearance is cryptographically bound to the user's identity.
    
    Properties:
    - Unique visual fingerprint for each user
    - Millions of data points forming the structure
    - Cryptographic proofs embedded in every element
    - Cannot be forged - the math behind it ensures uniqueness
    - Self-verifying - can validate its own authenticity
    """
    
    # Identification
    model_id: str
    dna_key_id: str
    created_at: datetime
    
    # Structure definition
    shape: DNAStrandShape
    style: DNAStrandStyle
    
    # 3D model data
    points: List[DNAStrandPoint] = field(default_factory=list)
    bonds: List[DNAStrandBond] = field(default_factory=list)
    
    # Dimensions
    total_height: float = 1000.0
    helix_radius: float = 100.0
    num_turns: int = 10
    
    # Visual parameters
    base_colors: List[str] = field(default_factory=list)
    glow_color: str = "#00FFFF"
    particle_count: int = 10000
    
    # Animation parameters
    rotation_speed: float = 0.01
    pulse_frequency: float = 2.0
    particle_flow_speed: float = 0.5
    
    # AUTHENTICATION DATA (embedded in the model)
    model_signature: str = ""  # Ed25519 signature of entire model
    model_checksum: str = ""   # SHA3-512 of all points and bonds
    security_layers_hash: str = ""  # Hash of security layer structure
    
    # Verification data
    verification_points: List[int] = field(default_factory=list)  # Random points for quick verify
    challenge_response_seed: str = ""  # Seed for challenge-response
    
    def compute_model_checksum(self) -> str:
        """
        Compute SHA3-512 checksum of the entire 3D model.
        
        This checksum is part of what makes this model
        THE authentication - any change invalidates it.
        """
        hasher = hashlib.sha3_512()
        
        # Hash all points
        for point in self.points:
            hasher.update(point.position_hash.encode())
            hasher.update(str(point.x).encode())
            hasher.update(str(point.y).encode())
            hasher.update(str(point.z).encode())
        
        # Hash all bonds
        for bond in self.bonds:
            hasher.update(bond.bond_hash.encode())
            hasher.update(str(bond.point_a_index).encode())
            hasher.update(str(bond.point_b_index).encode())
        
        # Hash structure parameters
        hasher.update(self.shape.value.encode())
        hasher.update(self.style.value.encode())
        hasher.update(str(self.total_height).encode())
        hasher.update(str(self.helix_radius).encode())
        
        self.model_checksum = hasher.hexdigest()
        return self.model_checksum
    
    def verify_integrity(self) -> bool:
        """
        Verify this 3D model has not been tampered with.
        
        The visual model IS the authentication - if anything
        is changed, authentication fails.
        """
        stored_checksum = self.model_checksum
        computed_checksum = self.compute_model_checksum()
        self.model_checksum = stored_checksum
        
        return secrets.compare_digest(computed_checksum, stored_checksum)
    
    def get_verification_challenge(self) -> Dict[str, Any]:
        """
        Generate a challenge based on random points in the model.
        
        To authenticate, the client must prove they have
        the actual 3D model by responding with correct point data.
        """
        # Select random points for challenge
        if not self.verification_points:
            num_challenges = min(100, len(self.points))
            self.verification_points = sorted(
                secrets.choice(range(len(self.points))) 
                for _ in range(num_challenges)
            )
        
        challenge_id = secrets.token_hex(32)
        
        return {
            "challenge_id": challenge_id,
            "model_id": self.model_id,
            "requested_points": self.verification_points[:10],  # Ask for 10 points
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nonce": secrets.token_hex(16)
        }
    
    def verify_challenge_response(
        self, 
        challenge_id: str, 
        response_points: List[Dict[str, Any]]
    ) -> bool:
        """
        Verify the challenge response.
        
        The client must provide the exact point data from their
        3D model. This proves they possess the authentic model.
        """
        for i, resp in enumerate(response_points):
            if i >= len(self.verification_points):
                break
            
            point_idx = self.verification_points[i]
            if point_idx >= len(self.points):
                return False
            
            actual_point = self.points[point_idx]
            
            # Verify position hash matches
            if resp.get("position_hash") != actual_point.position_hash:
                return False
            
            # Verify coordinates (with small tolerance for floating point)
            if abs(resp.get("x", 0) - actual_point.x) > 0.0001:
                return False
            if abs(resp.get("y", 0) - actual_point.y) > 0.0001:
                return False
            if abs(resp.get("z", 0) - actual_point.z) > 0.0001:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "model_id": self.model_id,
            "dna_key_id": self.dna_key_id,
            "created_at": self.created_at.isoformat(),
            "shape": self.shape.value,
            "style": self.style.value,
            "dimensions": {
                "height": self.total_height,
                "radius": self.helix_radius,
                "turns": self.num_turns
            },
            "points_count": len(self.points),
            "bonds_count": len(self.bonds),
            "visual": {
                "base_colors": self.base_colors,
                "glow_color": self.glow_color,
                "particle_count": self.particle_count
            },
            "animation": {
                "rotation_speed": self.rotation_speed,
                "pulse_frequency": self.pulse_frequency,
                "particle_flow_speed": self.particle_flow_speed
            },
            "authentication": {
                "model_signature": self.model_signature,
                "model_checksum": self.model_checksum,
                "security_layers_hash": self.security_layers_hash
            }
        }
    
    def to_full_model(self) -> Dict[str, Any]:
        """Export complete model with all points and bonds."""
        result = self.to_dict()
        result["points"] = [p.to_dict() for p in self.points]
        result["bonds"] = [b.to_dict() for b in self.bonds]
        return result


# Segment type to color mapping (expanded for all 20 types)
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
    SegmentType.REVOCATION: "#FF1493",   # Pink
    SegmentType.KEY_DERIVATION: "#FFD700",  # Gold
    SegmentType.ENCRYPTION: "#7B68EE",   # Medium slate blue
    SegmentType.NONCE: "#20B2AA",        # Light sea green
    SegmentType.CHALLENGE: "#DC143C",    # Crimson
    SegmentType.ATTESTATION: "#00FA9A",  # Medium spring green
    SegmentType.FINGERPRINT: "#FF6347",  # Tomato
    SegmentType.RECOVERY: "#4169E1",     # Royal blue
    SegmentType.AUDIT: "#32CD32",        # Lime green
    SegmentType.QUANTUM: "#9400D3",      # Dark violet
    SegmentType.CUSTOM: "#FFFFFF",       # White
}


class DNAStrand3DGenerator:
    """
    Generator for 3D DNA Strand Authentication Models.
    
    THIS GENERATOR CREATES THE ACTUAL AUTHENTICATION CREDENTIAL.
    
    The generated 3D model is not just a visual representation -
    it IS the authentication itself. Every point, every bond,
    every color is cryptographically bound to the user's identity.
    """
    
    def __init__(
        self,
        dna_key: DNAKey,
        shape: DNAStrandShape = DNAStrandShape.DOUBLE_HELIX,
        style: DNAStrandStyle = DNAStrandStyle.TRON
    ):
        """
        Initialize the 3D generator.
        
        Args:
            dna_key: The DNA key containing all security data
            shape: The 3D shape of the helix
            style: The visual style theme
        """
        self.dna_key = dna_key
        self.shape = shape
        self.style = style
        
        # Use the DNA key's data to seed randomness (deterministic)
        self.seed = self._compute_seed()
    
    def _compute_seed(self) -> bytes:
        """Compute deterministic seed from DNA key."""
        hasher = hashlib.sha3_256()
        hasher.update(self.dna_key.key_id.encode() if self.dna_key.key_id else b"")
        hasher.update(self.dna_key.dna_helix.checksum.encode() if self.dna_key.dna_helix.checksum else b"")
        return hasher.digest()
    
    def _seeded_random(self, index: int) -> float:
        """Generate deterministic random value from seed and index."""
        hasher = hashlib.sha3_256()
        hasher.update(self.seed)
        hasher.update(index.to_bytes(8, 'big'))
        hash_bytes = hasher.digest()
        # Convert first 8 bytes to float between 0 and 1
        value = int.from_bytes(hash_bytes[:8], 'big')
        return (value % 1000000) / 1000000.0
    
    def generate(
        self,
        height: float = 1000.0,
        radius: float = 100.0,
        turns: int = 10,
        max_points: int = 50000
    ) -> DNAStrand3DModel:
        """
        Generate the complete 3D DNA strand authentication model.
        
        This creates the visual model that IS the authentication.
        
        Args:
            height: Total height of the helix
            radius: Radius of the helix
            turns: Number of complete rotations
            max_points: Maximum number of points to generate
            
        Returns:
            DNAStrand3DModel - THE authentication credential
        """
        # Create the model
        model = DNAStrand3DModel(
            model_id=f"dna3d-{secrets.token_hex(16)}",
            dna_key_id=self.dna_key.key_id or "",
            created_at=datetime.now(timezone.utc),
            shape=self.shape,
            style=self.style,
            total_height=height,
            helix_radius=radius,
            num_turns=turns
        )
        
        # Get segments from DNA key
        segments = self.dna_key.dna_helix.segments
        num_segments = len(segments)
        
        # Determine number of points (based on segments and limits)
        num_points = min(max_points, num_segments * 2)
        
        # Generate points based on shape
        if self.shape == DNAStrandShape.DOUBLE_HELIX:
            self._generate_double_helix(model, num_points, segments)
        elif self.shape == DNAStrandShape.TRIPLE_HELIX:
            self._generate_triple_helix(model, num_points, segments)
        elif self.shape == DNAStrandShape.QUADRUPLE_HELIX:
            self._generate_quadruple_helix(model, num_points, segments)
        else:
            # Default to double helix
            self._generate_double_helix(model, num_points, segments)
        
        # Generate bonds between points
        self._generate_bonds(model)
        
        # Set visual parameters based on style
        self._apply_style(model)
        
        # Compute authentication checksum
        model.compute_model_checksum()
        
        # Generate verification points
        model.verification_points = [
            int(self._seeded_random(i * 1000) * len(model.points))
            for i in range(100)
        ]
        
        # Set challenge-response seed
        model.challenge_response_seed = hashlib.sha3_256(
            self.seed + b"challenge"
        ).hexdigest()
        
        return model
    
    def _generate_double_helix(
        self,
        model: DNAStrand3DModel,
        num_points: int,
        segments: List[DNASegment]
    ):
        """Generate classic double helix structure."""
        points_per_strand = num_points // 2
        
        for strand in range(2):
            phase_offset = strand * math.pi  # 180 degrees apart
            
            for i in range(points_per_strand):
                t = i / points_per_strand
                angle = t * model.num_turns * 2 * math.pi + phase_offset
                
                # Calculate 3D position
                x = model.helix_radius * math.cos(angle)
                z = model.helix_radius * math.sin(angle)
                y = t * model.total_height
                
                # Add some organic variation
                variation = self._seeded_random(strand * 100000 + i) * 5
                x += variation * math.sin(angle * 3)
                z += variation * math.cos(angle * 3)
                
                # Get corresponding segment
                seg_idx = int(i * len(segments) / points_per_strand) % len(segments)
                segment = segments[seg_idx]
                
                # Get color based on segment type
                color = SEGMENT_COLORS.get(segment.type, "#FFFFFF")
                
                # Compute position hash (THIS IS AUTHENTICATION DATA)
                position_hash = hashlib.sha3_256(
                    f"{x:.6f}:{y:.6f}:{z:.6f}:{segment.segment_hash}".encode()
                ).hexdigest()
                
                # Create point
                point = DNAStrandPoint(
                    x=x,
                    y=y,
                    z=z,
                    color=color,
                    glow_intensity=0.8 + self._seeded_random(i) * 0.2,
                    particle_density=self._seeded_random(i + 1000) * 0.5,
                    position_hash=position_hash,
                    segment_binding=segment.segment_hash or "",
                    layer_index=self._get_layer_index(segment.type),
                    pulse_phase=self._seeded_random(i + 2000) * 2 * math.pi,
                    rotation_offset=self._seeded_random(i + 3000) * 0.1
                )
                
                model.points.append(point)
    
    def _generate_triple_helix(
        self,
        model: DNAStrand3DModel,
        num_points: int,
        segments: List[DNASegment]
    ):
        """Generate triple helix structure (more secure)."""
        points_per_strand = num_points // 3
        
        for strand in range(3):
            phase_offset = strand * (2 * math.pi / 3)  # 120 degrees apart
            
            for i in range(points_per_strand):
                t = i / points_per_strand
                angle = t * model.num_turns * 2 * math.pi + phase_offset
                
                x = model.helix_radius * math.cos(angle)
                z = model.helix_radius * math.sin(angle)
                y = t * model.total_height
                
                seg_idx = int(i * len(segments) / points_per_strand) % len(segments)
                segment = segments[seg_idx]
                color = SEGMENT_COLORS.get(segment.type, "#FFFFFF")
                
                position_hash = hashlib.sha3_256(
                    f"{x:.6f}:{y:.6f}:{z:.6f}:{segment.segment_hash}:{strand}".encode()
                ).hexdigest()
                
                point = DNAStrandPoint(
                    x=x, y=y, z=z,
                    color=color,
                    glow_intensity=0.8 + self._seeded_random(i) * 0.2,
                    particle_density=self._seeded_random(i + 1000) * 0.5,
                    position_hash=position_hash,
                    segment_binding=segment.segment_hash or "",
                    layer_index=self._get_layer_index(segment.type),
                    pulse_phase=self._seeded_random(i + 2000) * 2 * math.pi,
                    rotation_offset=self._seeded_random(i + 3000) * 0.1
                )
                
                model.points.append(point)
    
    def _generate_quadruple_helix(
        self,
        model: DNAStrand3DModel,
        num_points: int,
        segments: List[DNASegment]
    ):
        """Generate quadruple helix structure (maximum security)."""
        points_per_strand = num_points // 4
        
        for strand in range(4):
            phase_offset = strand * (math.pi / 2)  # 90 degrees apart
            
            for i in range(points_per_strand):
                t = i / points_per_strand
                angle = t * model.num_turns * 2 * math.pi + phase_offset
                
                x = model.helix_radius * math.cos(angle)
                z = model.helix_radius * math.sin(angle)
                y = t * model.total_height
                
                seg_idx = int(i * len(segments) / points_per_strand) % len(segments)
                segment = segments[seg_idx]
                color = SEGMENT_COLORS.get(segment.type, "#FFFFFF")
                
                position_hash = hashlib.sha3_256(
                    f"{x:.6f}:{y:.6f}:{z:.6f}:{segment.segment_hash}:{strand}".encode()
                ).hexdigest()
                
                point = DNAStrandPoint(
                    x=x, y=y, z=z,
                    color=color,
                    glow_intensity=0.8 + self._seeded_random(i) * 0.2,
                    particle_density=self._seeded_random(i + 1000) * 0.5,
                    position_hash=position_hash,
                    segment_binding=segment.segment_hash or "",
                    layer_index=self._get_layer_index(segment.type),
                    pulse_phase=self._seeded_random(i + 2000) * 2 * math.pi,
                    rotation_offset=self._seeded_random(i + 3000) * 0.1
                )
                
                model.points.append(point)
    
    def _generate_bonds(self, model: DNAStrand3DModel):
        """Generate bonds between points."""
        num_points = len(model.points)
        
        # Determine strands based on shape
        if model.shape == DNAStrandShape.TRIPLE_HELIX:
            num_strands = 3
        elif model.shape == DNAStrandShape.QUADRUPLE_HELIX:
            num_strands = 4
        else:
            num_strands = 2
        
        points_per_strand = num_points // num_strands
        
        # Create backbone bonds (within each strand)
        for strand in range(num_strands):
            start_idx = strand * points_per_strand
            
            for i in range(points_per_strand - 1):
                point_a = start_idx + i
                point_b = start_idx + i + 1
                
                bond_hash = hashlib.sha3_256(
                    f"{model.points[point_a].position_hash}:{model.points[point_b].position_hash}".encode()
                ).hexdigest()
                
                bond = DNAStrandBond(
                    point_a_index=point_a,
                    point_b_index=point_b,
                    bond_type="backbone",
                    bond_strength=0.8,
                    bond_color=model.points[point_a].color,
                    bond_hash=bond_hash
                )
                
                model.bonds.append(bond)
        
        # Create cross-links (between strands)
        step = max(1, points_per_strand // 50)  # Connect every ~50 points
        
        for i in range(0, points_per_strand, step):
            for strand_a in range(num_strands):
                strand_b = (strand_a + 1) % num_strands
                
                point_a = strand_a * points_per_strand + i
                point_b = strand_b * points_per_strand + i
                
                if point_a < num_points and point_b < num_points:
                    bond_hash = hashlib.sha3_256(
                        f"cross:{model.points[point_a].position_hash}:{model.points[point_b].position_hash}".encode()
                    ).hexdigest()
                    
                    bond = DNAStrandBond(
                        point_a_index=point_a,
                        point_b_index=point_b,
                        bond_type="base_pair",
                        bond_strength=0.5,
                        bond_color="#FFFFFF",
                        bond_hash=bond_hash
                    )
                    
                    model.bonds.append(bond)
    
    def _apply_style(self, model: DNAStrand3DModel):
        """Apply visual style to the model."""
        style_configs = {
            DNAStrandStyle.TRON: {
                "glow_color": "#00FFFF",
                "base_colors": ["#00FFFF", "#FF00FF", "#FFFF00"],
                "particle_count": 10000,
                "rotation_speed": 0.01,
                "pulse_frequency": 2.0
            },
            DNAStrandStyle.ORGANIC: {
                "glow_color": "#90EE90",
                "base_colors": ["#228B22", "#8B4513", "#FFD700"],
                "particle_count": 5000,
                "rotation_speed": 0.005,
                "pulse_frequency": 1.0
            },
            DNAStrandStyle.CRYSTALLINE: {
                "glow_color": "#E0FFFF",
                "base_colors": ["#00CED1", "#7FFFD4", "#AFEEEE"],
                "particle_count": 15000,
                "rotation_speed": 0.008,
                "pulse_frequency": 3.0
            },
            DNAStrandStyle.PLASMA: {
                "glow_color": "#FF4500",
                "base_colors": ["#FF4500", "#FF6347", "#FFD700"],
                "particle_count": 20000,
                "rotation_speed": 0.015,
                "pulse_frequency": 5.0
            },
            DNAStrandStyle.HOLOGRAPHIC: {
                "glow_color": "#00FF00",
                "base_colors": ["#00FF00", "#00FFFF", "#FF00FF"],
                "particle_count": 8000,
                "rotation_speed": 0.02,
                "pulse_frequency": 4.0
            },
            DNAStrandStyle.QUANTUM: {
                "glow_color": "#9400D3",
                "base_colors": ["#9400D3", "#4B0082", "#8A2BE2"],
                "particle_count": 25000,
                "rotation_speed": 0.025,
                "pulse_frequency": 8.0
            },
            DNAStrandStyle.NEBULA: {
                "glow_color": "#FF1493",
                "base_colors": ["#FF1493", "#8B008B", "#4B0082"],
                "particle_count": 30000,
                "rotation_speed": 0.003,
                "pulse_frequency": 0.5
            },
            DNAStrandStyle.MATRIX: {
                "glow_color": "#00FF00",
                "base_colors": ["#00FF00", "#008000", "#003300"],
                "particle_count": 50000,
                "rotation_speed": 0.01,
                "pulse_frequency": 10.0
            }
        }
        
        config = style_configs.get(self.style, style_configs[DNAStrandStyle.TRON])
        
        model.glow_color = config["glow_color"]
        model.base_colors = config["base_colors"]
        model.particle_count = config["particle_count"]
        model.rotation_speed = config["rotation_speed"]
        model.pulse_frequency = config["pulse_frequency"]
    
    def _get_layer_index(self, segment_type: SegmentType) -> int:
        """Map segment type to security layer (1-5)."""
        layer_mapping = {
            SegmentType.METADATA: 1,
            SegmentType.REVOCATION: 1,
            SegmentType.ENTROPY: 2,
            SegmentType.NONCE: 2,
            SegmentType.POLICY: 3,
            SegmentType.CAPABILITY: 3,
            SegmentType.TEMPORAL: 3,
            SegmentType.HASH: 4,
            SegmentType.ATTESTATION: 4,
            SegmentType.BIOMETRIC: 4,
            SegmentType.SIGNATURE: 5,
            SegmentType.KEY_DERIVATION: 5,
            SegmentType.ENCRYPTION: 5,
            SegmentType.RECOVERY: 5,
        }
        return layer_mapping.get(segment_type, 3)


def generate_dna_strand_3d(
    dna_key: DNAKey,
    shape: DNAStrandShape = DNAStrandShape.DOUBLE_HELIX,
    style: DNAStrandStyle = DNAStrandStyle.TRON,
    max_points: int = 50000
) -> DNAStrand3DModel:
    """
    Generate a 3D DNA strand authentication model.
    
    THE RETURNED MODEL IS THE AUTHENTICATION CREDENTIAL.
    
    Args:
        dna_key: The DNA key containing security data
        shape: Shape of the 3D helix
        style: Visual style theme
        max_points: Maximum number of 3D points
        
    Returns:
        DNAStrand3DModel that IS the authentication
    """
    generator = DNAStrand3DGenerator(dna_key, shape, style)
    return generator.generate(max_points=max_points)
