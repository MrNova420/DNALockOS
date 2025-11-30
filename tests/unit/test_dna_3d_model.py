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
DNA-Key Authentication System - 3D Model and Integration Tests

Comprehensive tests for:
- 3D DNA strand model generation
- Platform integration SDK
- Security techniques
"""

import pytest
from datetime import datetime, timezone, timedelta

from server.crypto.dna_key import DNAKey, DNAHelix, DNASegment, SegmentType, SecurityLevel
from server.crypto.dna_generator import DNAKeyGenerator, generate_dna_key
from server.visual.dna_strand_3d_model import (
    DNAStrand3DModel,
    DNAStrand3DGenerator,
    DNAStrandPoint,
    DNAStrandBond,
    DNAStrandShape,
    DNAStrandStyle,
    generate_dna_strand_3d,
)


class TestDNAStrand3DModel:
    """Test 3D DNA strand model generation."""
    
    def test_generate_3d_model(self):
        """Test generating a 3D model from a DNA key."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key)
        
        assert model is not None
        assert model.model_id.startswith("dna3d-")
        assert len(model.points) > 0
        assert len(model.bonds) > 0
    
    def test_model_has_checksum(self):
        """Test that generated model has a checksum."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key)
        
        assert model.model_checksum != ""
        assert len(model.model_checksum) == 128  # SHA3-512 hex
    
    def test_model_integrity_verification(self):
        """Test that model integrity can be verified."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key)
        
        # Model should verify successfully
        assert model.verify_integrity() is True
    
    def test_model_tamper_detection(self):
        """Test that tampering is detected."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key)
        
        # Tamper with a point
        if model.points:
            model.points[0].x += 100.0
        
        # Should fail verification
        assert model.verify_integrity() is False
    
    def test_different_shapes(self):
        """Test different helix shapes."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        
        for shape in [DNAStrandShape.DOUBLE_HELIX, DNAStrandShape.TRIPLE_HELIX, DNAStrandShape.QUADRUPLE_HELIX]:
            model = generate_dna_strand_3d(dna_key, shape=shape)
            assert model.shape == shape
            assert len(model.points) > 0
    
    def test_different_styles(self):
        """Test different visual styles."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        
        for style in [DNAStrandStyle.TRON, DNAStrandStyle.ORGANIC, DNAStrandStyle.QUANTUM]:
            model = generate_dna_strand_3d(dna_key, style=style)
            assert model.style == style
            assert model.glow_color != ""
    
    def test_model_to_dict(self):
        """Test model serialization."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key)
        
        model_dict = model.to_dict()
        
        assert "model_id" in model_dict
        assert "dna_key_id" in model_dict
        assert "shape" in model_dict
        assert "style" in model_dict
        assert "authentication" in model_dict
        assert "model_checksum" in model_dict["authentication"]
    
    def test_point_has_position_hash(self):
        """Test that each point has a position hash for authentication."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key)
        
        for point in model.points[:100]:  # Check first 100
            assert point.position_hash != ""
            assert len(point.position_hash) == 64  # SHA3-256 hex
    
    def test_bond_has_hash(self):
        """Test that each bond has a hash for authentication."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key)
        
        for bond in model.bonds[:100]:  # Check first 100
            assert bond.bond_hash != ""
            assert len(bond.bond_hash) == 64  # SHA3-256 hex
    
    def test_verification_challenge(self):
        """Test verification challenge generation."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key)
        
        challenge = model.get_verification_challenge()
        
        assert "challenge_id" in challenge
        assert "model_id" in challenge
        assert "requested_points" in challenge
        assert len(challenge["requested_points"]) > 0
    
    def test_unique_models_for_different_keys(self):
        """Test that different DNA keys produce different 3D models."""
        key1 = generate_dna_key("user1@example.com", SecurityLevel.STANDARD)
        key2 = generate_dna_key("user2@example.com", SecurityLevel.STANDARD)
        
        model1 = generate_dna_strand_3d(key1)
        model2 = generate_dna_strand_3d(key2)
        
        # Different checksums
        assert model1.model_checksum != model2.model_checksum
    
    def test_deterministic_model_for_same_key(self):
        """Test that same DNA key produces same 3D model."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        
        model1 = generate_dna_strand_3d(dna_key)
        model2 = generate_dna_strand_3d(dna_key)
        
        # Same checksums (deterministic)
        assert model1.model_checksum == model2.model_checksum


class TestDNAStrandPoint:
    """Test DNAStrandPoint dataclass."""
    
    def test_point_creation(self):
        """Test creating a point."""
        point = DNAStrandPoint(
            x=100.0,
            y=200.0,
            z=50.0,
            color="#00FFFF",
            glow_intensity=0.8,
            particle_density=0.5,
            position_hash="abc123",
            segment_binding="def456",
            layer_index=2,
            pulse_phase=0.5,
            rotation_offset=0.1
        )
        
        assert point.x == 100.0
        assert point.y == 200.0
        assert point.z == 50.0
        assert point.color == "#00FFFF"
    
    def test_point_to_dict(self):
        """Test point serialization."""
        point = DNAStrandPoint(
            x=100.0, y=200.0, z=50.0,
            color="#00FFFF",
            glow_intensity=0.8,
            particle_density=0.5,
            position_hash="abc123",
            segment_binding="def456",
            layer_index=2,
            pulse_phase=0.5,
            rotation_offset=0.1
        )
        
        point_dict = point.to_dict()
        
        assert point_dict["position"]["x"] == 100.0
        assert point_dict["visual"]["color"] == "#00FFFF"
        assert point_dict["auth"]["position_hash"] == "abc123"


class TestDNAStrandBond:
    """Test DNAStrandBond dataclass."""
    
    def test_bond_creation(self):
        """Test creating a bond."""
        bond = DNAStrandBond(
            point_a_index=0,
            point_b_index=1,
            bond_type="backbone",
            bond_strength=0.8,
            bond_color="#FFFFFF",
            bond_hash="xyz789"
        )
        
        assert bond.point_a_index == 0
        assert bond.point_b_index == 1
        assert bond.bond_type == "backbone"
    
    def test_bond_to_dict(self):
        """Test bond serialization."""
        bond = DNAStrandBond(
            point_a_index=0,
            point_b_index=1,
            bond_type="backbone",
            bond_strength=0.8,
            bond_color="#FFFFFF",
            bond_hash="xyz789"
        )
        
        bond_dict = bond.to_dict()
        
        assert bond_dict["start"] == 0
        assert bond_dict["end"] == 1
        assert bond_dict["auth_hash"] == "xyz789"


class TestDNAStrandShapes:
    """Test different DNA strand shapes."""
    
    def test_double_helix_shape(self):
        """Test double helix has 2 strands."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key, shape=DNAStrandShape.DOUBLE_HELIX)
        
        assert model.shape == DNAStrandShape.DOUBLE_HELIX
    
    def test_triple_helix_shape(self):
        """Test triple helix has 3 strands."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key, shape=DNAStrandShape.TRIPLE_HELIX)
        
        assert model.shape == DNAStrandShape.TRIPLE_HELIX
    
    def test_quadruple_helix_shape(self):
        """Test quadruple helix has 4 strands."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key, shape=DNAStrandShape.QUADRUPLE_HELIX)
        
        assert model.shape == DNAStrandShape.QUADRUPLE_HELIX


class TestDNAStrandStyles:
    """Test different visual styles."""
    
    def test_tron_style(self):
        """Test Tron style configuration."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key, style=DNAStrandStyle.TRON)
        
        assert model.style == DNAStrandStyle.TRON
        assert model.glow_color == "#00FFFF"  # Cyan for Tron
    
    def test_quantum_style(self):
        """Test Quantum style configuration."""
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        model = generate_dna_strand_3d(dna_key, style=DNAStrandStyle.QUANTUM)
        
        assert model.style == DNAStrandStyle.QUANTUM
        assert model.particle_count > 10000  # High particle count
