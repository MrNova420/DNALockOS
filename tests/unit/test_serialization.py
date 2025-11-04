"""
DNA-Key Authentication System - CBOR Serialization Tests

Comprehensive test suite for CBOR serialization.
Tests cover:
- Serialization and deserialization
- Round-trip consistency
- Size optimization
- Edge cases
"""

import pytest
from server.crypto.dna_generator import generate_dna_key, SecurityLevel
from server.crypto.serialization import (
    DNAKeySerializer,
    serialize_dna_key,
    deserialize_dna_key
)
from server.crypto.dna_key import DNAKey, DNASegment, SegmentType, DNAHelix


class TestCBORSerialization:
    """Test CBOR serialization."""
    
    def test_serialize_standard_key(self):
        """Test serializing a standard DNA key."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        
        cbor_data = DNAKeySerializer.serialize(key)
        
        assert isinstance(cbor_data, bytes)
        assert len(cbor_data) > 0
    
    def test_deserialize_standard_key(self):
        """Test deserializing a standard DNA key."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = DNAKeySerializer.serialize(key)
        
        restored_key = DNAKeySerializer.deserialize(cbor_data)
        
        assert isinstance(restored_key, DNAKey)
    
    def test_round_trip_key_id(self):
        """Test that key ID survives round trip."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = DNAKeySerializer.serialize(key)
        restored_key = DNAKeySerializer.deserialize(cbor_data)
        
        assert restored_key.key_id == key.key_id
    
    def test_round_trip_segment_count(self):
        """Test that segment count survives round trip."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = DNAKeySerializer.serialize(key)
        restored_key = DNAKeySerializer.deserialize(cbor_data)
        
        assert restored_key.dna_helix.segment_count == key.dna_helix.segment_count
    
    def test_round_trip_checksum(self):
        """Test that checksum survives round trip."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = DNAKeySerializer.serialize(key)
        restored_key = DNAKeySerializer.deserialize(cbor_data)
        
        assert restored_key.dna_helix.checksum == key.dna_helix.checksum
    
    def test_round_trip_subject_info(self):
        """Test that subject info survives round trip."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = DNAKeySerializer.serialize(key)
        restored_key = DNAKeySerializer.deserialize(cbor_data)
        
        assert restored_key.subject.subject_id == key.subject.subject_id
        assert restored_key.subject.subject_type == key.subject.subject_type
    
    def test_round_trip_policy_binding(self):
        """Test that policy binding survives round trip."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = DNAKeySerializer.serialize(key)
        restored_key = DNAKeySerializer.deserialize(cbor_data)
        
        assert restored_key.policy_binding.policy_id == key.policy_binding.policy_id
        assert restored_key.policy_binding.mfa_required == key.policy_binding.mfa_required
    
    def test_round_trip_crypto_material(self):
        """Test that cryptographic material survives round trip."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = DNAKeySerializer.serialize(key)
        restored_key = DNAKeySerializer.deserialize(cbor_data)
        
        assert restored_key.cryptographic_material.algorithm == key.cryptographic_material.algorithm
        assert restored_key.cryptographic_material.public_key == key.cryptographic_material.public_key
    
    def test_round_trip_visual_dna(self):
        """Test that visual DNA survives round trip."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = DNAKeySerializer.serialize(key)
        restored_key = DNAKeySerializer.deserialize(cbor_data)
        
        assert restored_key.visual_dna.color_palette == key.visual_dna.color_palette
        assert restored_key.visual_dna.helix_rotation == key.visual_dna.helix_rotation
        assert restored_key.visual_dna.animation_seed == key.visual_dna.animation_seed
    
    def test_round_trip_segments(self):
        """Test that all segments survive round trip."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = DNAKeySerializer.serialize(key)
        restored_key = DNAKeySerializer.deserialize(cbor_data)
        
        assert len(restored_key.dna_helix.segments) == len(key.dna_helix.segments)
        
        # Check a few random segments
        for i in [0, 100, 500]:
            orig_seg = key.dna_helix.segments[i]
            restored_seg = restored_key.dna_helix.segments[i]
            
            assert restored_seg.position == orig_seg.position
            assert restored_seg.type == orig_seg.type
            assert restored_seg.data == orig_seg.data


class TestSerializationSizes:
    """Test serialization size optimization."""
    
    def test_standard_key_size(self):
        """Test that standard key serializes to reasonable size."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        
        size = DNAKeySerializer.get_serialized_size(key)
        
        # Standard key (1024 segments) should be < 200KB
        assert size < 200 * 1024
        print(f"Standard key size: {size / 1024:.1f} KB")
    
    def test_enhanced_key_size(self):
        """Test enhanced key size."""
        key = generate_dna_key("user@example.com", SecurityLevel.ENHANCED)
        
        size = DNAKeySerializer.get_serialized_size(key)
        
        # Enhanced key (16384 segments) should be < 3MB
        assert size < 3 * 1024 * 1024
        print(f"Enhanced key size: {size / (1024 * 1024):.2f} MB")
    
    def test_cbor_smaller_than_json(self):
        """Test that CBOR is smaller than JSON."""
        import json
        
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        
        cbor_size = DNAKeySerializer.get_serialized_size(key)
        json_size = len(json.dumps(key.to_dict()).encode())
        
        # CBOR should be at least 10% smaller than JSON
        # (Note: Our hex encoding limits compression, but CBOR is still more efficient)
        compression_ratio = (json_size - cbor_size) / json_size
        assert compression_ratio > 0.10
        print(f"CBOR compression: {compression_ratio * 100:.1f}% smaller than JSON")
        print(f"CBOR size: {cbor_size / 1024:.1f} KB, JSON size: {json_size / 1024:.1f} KB")


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_serialize_dna_key_function(self):
        """Test serialize_dna_key convenience function."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        
        cbor_data = serialize_dna_key(key)
        
        assert isinstance(cbor_data, bytes)
        assert len(cbor_data) > 0
    
    def test_deserialize_dna_key_function(self):
        """Test deserialize_dna_key convenience function."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = serialize_dna_key(key)
        
        restored_key = deserialize_dna_key(cbor_data)
        
        assert isinstance(restored_key, DNAKey)
        assert restored_key.key_id == key.key_id


class TestEdgeCases:
    """Test edge cases in serialization."""
    
    def test_serialize_minimal_key(self):
        """Test serializing a minimal DNA key."""
        key = DNAKey()
        key.dna_helix.segments = [
            DNASegment(0, SegmentType.ENTROPY, b"test")
        ]
        key.dna_helix.compute_checksum()
        
        cbor_data = serialize_dna_key(key)
        restored_key = deserialize_dna_key(cbor_data)
        
        assert restored_key.key_id == key.key_id
        assert restored_key.dna_helix.segment_count == 1
    
    def test_deterministic_serialization(self):
        """Test that serialization is deterministic."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        
        cbor1 = DNAKeySerializer.serialize(key)
        cbor2 = DNAKeySerializer.serialize(key)
        
        # Canonical CBOR should produce identical output
        assert cbor1 == cbor2
    
    def test_restored_key_is_valid(self):
        """Test that restored key passes validation."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = serialize_dna_key(key)
        restored_key = deserialize_dna_key(cbor_data)
        
        assert restored_key.is_valid()
    
    def test_restored_checksum_verifies(self):
        """Test that restored key checksum verifies."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = serialize_dna_key(key)
        restored_key = deserialize_dna_key(cbor_data)
        
        assert restored_key.dna_helix.verify_checksum()


class TestAllSecurityLevels:
    """Test serialization for all security levels."""
    
    def test_standard_level_round_trip(self):
        """Test standard security level."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        cbor_data = serialize_dna_key(key)
        restored_key = deserialize_dna_key(cbor_data)
        
        assert restored_key.dna_helix.segment_count == 1024
    
    def test_enhanced_level_round_trip(self):
        """Test enhanced security level."""
        key = generate_dna_key("user@example.com", SecurityLevel.ENHANCED)
        cbor_data = serialize_dna_key(key)
        restored_key = deserialize_dna_key(cbor_data)
        
        assert restored_key.dna_helix.segment_count == 16384
    
    def test_maximum_level_round_trip(self):
        """Test maximum security level."""
        key = generate_dna_key("user@example.com", SecurityLevel.MAXIMUM)
        cbor_data = serialize_dna_key(key)
        restored_key = deserialize_dna_key(cbor_data)
        
        assert restored_key.dna_helix.segment_count == 65536


class TestSegmentTypes:
    """Test that all segment types serialize correctly."""
    
    def test_all_segment_types_preserved(self):
        """Test that all segment types are preserved."""
        key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        
        # Get original type counts
        orig_types = {}
        for seg in key.dna_helix.segments:
            orig_types[seg.type] = orig_types.get(seg.type, 0) + 1
        
        # Serialize and deserialize
        cbor_data = serialize_dna_key(key)
        restored_key = deserialize_dna_key(cbor_data)
        
        # Get restored type counts
        restored_types = {}
        for seg in restored_key.dna_helix.segments:
            restored_types[seg.type] = restored_types.get(seg.type, 0) + 1
        
        # Should match
        assert orig_types == restored_types
