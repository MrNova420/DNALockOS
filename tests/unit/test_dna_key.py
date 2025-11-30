"""
DNA-Key Authentication System - DNA Key Model and Generation Tests

Comprehensive test suite for DNA key data models and generation.
Tests cover:
- DNA segment creation and validation
- DNA helix structure and checksums
- DNA key generation with various security levels
- Segment distribution and shuffling
- Key validation and expiration
- Multi-layer security architecture
- Security methods integration
- Custom verification system
"""

import pytest
from datetime import datetime, timezone, timedelta

from server.crypto.dna_key import (
    DNAKey,
    DNAHelix,
    DNASegment,
    SegmentType,
    SecurityLevel,
    SecurityLayer,
    SecurityMethodsIntegrated,
    LayerChecksum,
    IssuerInfo,
    SubjectInfo,
    CryptographicMaterial,
    PolicyBinding,
    VisualDNA
)
from server.crypto.dna_generator import (
    DNAKeyGenerator,
    generate_dna_key
)


class TestDNASegment:
    """Test DNA segment creation and validation."""
    
    def test_create_segment(self):
        """Test creating a DNA segment."""
        segment = DNASegment(
            position=0,
            type=SegmentType.ENTROPY,
            data=b"test data"
        )
        
        assert segment.position == 0
        assert segment.type == SegmentType.ENTROPY
        assert segment.data == b"test data"
        assert segment.length == 9
        assert segment.segment_hash is not None
    
    def test_segment_hash_computed_automatically(self):
        """Test that segment hash is computed automatically."""
        segment = DNASegment(
            position=5,
            type=SegmentType.POLICY,
            data=b"policy data"
        )
        
        assert isinstance(segment.segment_hash, str)
        assert len(segment.segment_hash) == 64  # SHA3-256 hex
    
    def test_segment_hash_deterministic(self):
        """Test that segment hash is deterministic."""
        data = b"test data"
        seg1 = DNASegment(position=0, type=SegmentType.ENTROPY, data=data)
        seg2 = DNASegment(position=0, type=SegmentType.ENTROPY, data=data)
        
        assert seg1.segment_hash == seg2.segment_hash
    
    def test_different_data_different_hash(self):
        """Test that different data produces different hashes."""
        seg1 = DNASegment(position=0, type=SegmentType.ENTROPY, data=b"data1")
        seg2 = DNASegment(position=0, type=SegmentType.ENTROPY, data=b"data2")
        
        assert seg1.segment_hash != seg2.segment_hash
    
    def test_segment_to_dict(self):
        """Test converting segment to dictionary."""
        segment = DNASegment(
            position=10,
            type=SegmentType.TEMPORAL,
            data=b"timestamp"
        )
        
        seg_dict = segment.to_dict()
        
        assert seg_dict["position"] == 10
        assert seg_dict["type"] == "T"
        assert seg_dict["length"] == 9
        assert "segment_hash" in seg_dict


class TestDNAHelix:
    """Test DNA helix structure."""
    
    def test_create_empty_helix(self):
        """Test creating an empty DNA helix."""
        helix = DNAHelix()
        
        assert helix.segment_count == 0
        assert helix.strand_length == 0
        assert helix.checksum is None
    
    def test_helix_with_segments(self):
        """Test helix with segments."""
        segments = [
            DNASegment(0, SegmentType.ENTROPY, b"data1"),
            DNASegment(1, SegmentType.POLICY, b"data2"),
            DNASegment(2, SegmentType.HASH, b"data3")
        ]
        helix = DNAHelix(segments=segments)
        
        assert helix.segment_count == 3
        assert helix.strand_length == 15  # 5 + 5 + 5
    
    def test_compute_checksum(self):
        """Test computing helix checksum."""
        segments = [
            DNASegment(0, SegmentType.ENTROPY, b"data1"),
            DNASegment(1, SegmentType.POLICY, b"data2")
        ]
        helix = DNAHelix(segments=segments)
        
        checksum = helix.compute_checksum()
        
        assert isinstance(checksum, str)
        assert len(checksum) == 128  # SHA3-512 hex
        assert helix.checksum == checksum
    
    def test_checksum_deterministic(self):
        """Test that checksum is deterministic."""
        segments1 = [
            DNASegment(0, SegmentType.ENTROPY, b"data1"),
            DNASegment(1, SegmentType.POLICY, b"data2")
        ]
        segments2 = [
            DNASegment(0, SegmentType.ENTROPY, b"data1"),
            DNASegment(1, SegmentType.POLICY, b"data2")
        ]
        
        helix1 = DNAHelix(segments=segments1)
        helix2 = DNAHelix(segments=segments2)
        
        assert helix1.compute_checksum() == helix2.compute_checksum()
    
    def test_verify_checksum_valid(self):
        """Test verifying valid checksum."""
        segments = [DNASegment(0, SegmentType.ENTROPY, b"data")]
        helix = DNAHelix(segments=segments)
        helix.compute_checksum()
        
        assert helix.verify_checksum() is True
    
    def test_verify_checksum_invalid(self):
        """Test verifying invalid checksum."""
        segments = [DNASegment(0, SegmentType.ENTROPY, b"data")]
        helix = DNAHelix(segments=segments)
        helix.compute_checksum()
        
        # Tamper with segment
        helix.segments[0].data = b"tampered"
        
        assert helix.verify_checksum() is False
    
    def test_get_segments_by_type(self):
        """Test getting segments by type."""
        segments = [
            DNASegment(0, SegmentType.ENTROPY, b"e1"),
            DNASegment(1, SegmentType.POLICY, b"p1"),
            DNASegment(2, SegmentType.ENTROPY, b"e2"),
            DNASegment(3, SegmentType.HASH, b"h1")
        ]
        helix = DNAHelix(segments=segments)
        
        entropy_segs = helix.get_segments_by_type(SegmentType.ENTROPY)
        
        assert len(entropy_segs) == 2
        assert all(s.type == SegmentType.ENTROPY for s in entropy_segs)


class TestDNAKey:
    """Test DNA key structure."""
    
    def test_create_dna_key(self):
        """Test creating a DNA key."""
        key = DNAKey()
        
        assert key.format_version == "2.0"  # Updated to v2.0
        assert key.key_id is not None
        assert key.created_timestamp is not None
        assert isinstance(key.dna_helix, DNAHelix)
        assert isinstance(key.visual_dna, VisualDNA)
    
    def test_key_id_generated_automatically(self):
        """Test that key ID is generated automatically."""
        key = DNAKey()
        
        assert key.key_id.startswith("dna-")
        assert len(key.key_id) > 10
    
    def test_created_timestamp_set(self):
        """Test that created timestamp is set."""
        key = DNAKey()
        
        assert isinstance(key.created_timestamp, datetime)
        assert key.created_timestamp.tzinfo == timezone.utc
    
    def test_is_expired_no_expiry(self):
        """Test that key with no expiry is not expired."""
        key = DNAKey()
        
        assert key.is_expired() is False
    
    def test_is_expired_future(self):
        """Test that key with future expiry is not expired."""
        key = DNAKey()
        key.expires_timestamp = datetime.now(timezone.utc) + timedelta(days=365)
        
        assert key.is_expired() is False
    
    def test_is_expired_past(self):
        """Test that key with past expiry is expired."""
        key = DNAKey()
        key.expires_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
        
        assert key.is_expired() is True
    
    def test_is_valid_basic(self):
        """Test basic validity check."""
        key = DNAKey()
        # Add at least one segment
        key.dna_helix.segments.append(
            DNASegment(0, SegmentType.ENTROPY, b"data")
        )
        key.dna_helix.compute_checksum()
        
        assert key.is_valid() is True
    
    def test_is_valid_no_segments(self):
        """Test that key with no segments is invalid."""
        key = DNAKey()
        
        assert key.is_valid() is False
    
    def test_to_dict(self):
        """Test converting DNA key to dictionary."""
        key = DNAKey()
        key.dna_helix.segments.append(
            DNASegment(0, SegmentType.ENTROPY, b"data")
        )
        key.dna_helix.compute_checksum()
        
        key_dict = key.to_dict()
        
        assert "format_version" in key_dict
        assert "key_id" in key_dict
        assert "dna_helix" in key_dict
        assert "visual_dna" in key_dict


class TestDNAKeyGenerator:
    """Test DNA key generation."""
    
    def test_create_generator(self):
        """Test creating a DNA key generator."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        
        assert generator.security_level == SecurityLevel.STANDARD
        assert generator.segment_count == 1024
    
    def test_generate_standard_key(self):
        """Test generating a standard security level key."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        assert isinstance(key, DNAKey)
        assert key.dna_helix.segment_count == 1024
        assert key.is_valid()
    
    def test_generate_enhanced_key(self):
        """Test generating an enhanced security level key."""
        generator = DNAKeyGenerator(SecurityLevel.ENHANCED)
        key = generator.generate("user@example.com")
        
        assert key.dna_helix.segment_count == 16384
        assert key.is_valid()
    
    def test_generate_maximum_key(self):
        """Test generating a maximum security level key."""
        generator = DNAKeyGenerator(SecurityLevel.MAXIMUM)
        key = generator.generate("user@example.com")
        
        assert key.dna_helix.segment_count == 65536
        assert key.is_valid()
    
    def test_generated_key_has_all_components(self):
        """Test that generated key has all required components."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        assert key.key_id is not None
        assert key.created_timestamp is not None
        assert key.expires_timestamp is not None
        assert key.issuer is not None
        assert key.subject is not None
        assert key.cryptographic_material is not None
        assert key.policy_binding is not None
        assert key.dna_helix.checksum is not None
    
    def test_segment_distribution(self):
        """Test that segments are distributed according to spec."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        # Count segments by type
        type_counts = {}
        for segment in key.dna_helix.segments:
            seg_type = segment.type
            type_counts[seg_type] = type_counts.get(seg_type, 0) + 1
        
        total = sum(type_counts.values())
        
        # Check approximate distributions (within 1%)
        assert abs(type_counts.get(SegmentType.ENTROPY, 0) / total - 0.40) < 0.01
        assert abs(type_counts.get(SegmentType.POLICY, 0) / total - 0.10) < 0.01
        assert abs(type_counts.get(SegmentType.CAPABILITY, 0) / total - 0.20) < 0.01
    
    def test_expiration_set_correctly(self):
        """Test that expiration is set correctly."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com", validity_days=30)
        
        assert key.expires_timestamp is not None
        delta = key.expires_timestamp - key.created_timestamp
        
        # Should be approximately 30 days
        assert 29 <= delta.days <= 31
    
    def test_custom_policy_parameters(self):
        """Test generating key with custom policy parameters."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate(
            "user@example.com",
            mfa_required=True,
            biometric_required=True,
            device_binding_required=True
        )
        
        assert key.policy_binding.mfa_required is True
        assert key.policy_binding.biometric_required is True
        assert key.policy_binding.device_binding_required is True
    
    def test_unique_keys_generated(self):
        """Test that multiple generations produce unique keys."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        
        key1 = generator.generate("user1@example.com")
        key2 = generator.generate("user2@example.com")
        
        assert key1.key_id != key2.key_id
        assert key1.dna_helix.checksum != key2.dna_helix.checksum


class TestConvenienceFunction:
    """Test convenience function for key generation."""
    
    def test_generate_dna_key_function(self):
        """Test generate_dna_key convenience function."""
        key = generate_dna_key("user@example.com")
        
        assert isinstance(key, DNAKey)
        assert key.is_valid()
    
    def test_generate_with_security_level(self):
        """Test generating with different security level."""
        key = generate_dna_key("user@example.com", SecurityLevel.ENHANCED)
        
        assert key.dna_helix.segment_count == 16384
    
    def test_generate_with_custom_params(self):
        """Test generating with custom parameters."""
        key = generate_dna_key(
            "user@example.com",
            SecurityLevel.STANDARD,
            subject_type="device",
            policy_id="custom-policy",
            validity_days=90
        )
        
        assert key.subject.subject_type == "device"
        assert key.policy_binding.policy_id == "custom-policy"


class TestSegmentGeneration:
    """Test individual segment generation methods."""
    
    def test_entropy_segments_are_random(self):
        """Test that entropy segments contain random data."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        entropy_segs = key.dna_helix.get_segments_by_type(SegmentType.ENTROPY)
        
        # Check that entropy data varies
        data_set = set(seg.data for seg in entropy_segs[:10])
        assert len(data_set) == 10  # All unique
    
    def test_segments_have_position_markers(self):
        """Test that all segments have position markers."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        positions = [seg.position for seg in key.dna_helix.segments]
        
        assert len(positions) == len(set(positions))  # All unique
        assert max(positions) >= 0
    
    def test_segments_are_shuffled(self):
        """Test that segments are shuffled (not in sequential order)."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        positions = [seg.position for seg in key.dna_helix.segments]
        
        # If shuffled, positions won't be in order
        is_ordered = all(positions[i] <= positions[i+1] for i in range(len(positions)-1))
        
        # For 1024 segments, highly unlikely to be in order if shuffled
        assert not is_ordered


class TestSecurityLevels:
    """Test extended security levels including ULTIMATE."""
    
    def test_ultimate_security_level_exists(self):
        """Test that ULTIMATE security level is defined."""
        assert hasattr(SecurityLevel, 'ULTIMATE')
        assert SecurityLevel.ULTIMATE.value == "ultimate"
    
    def test_ultimate_security_level_segment_count(self):
        """Test ULTIMATE level has 1 million segments."""
        generator = DNAKeyGenerator(SecurityLevel.ULTIMATE)
        assert generator.segment_count == 1048576
    
    def test_all_security_levels(self):
        """Test all security levels have correct segment counts."""
        expected_counts = {
            SecurityLevel.STANDARD: 1024,
            SecurityLevel.ENHANCED: 16384,
            SecurityLevel.MAXIMUM: 65536,
            SecurityLevel.GOVERNMENT: 262144,
            SecurityLevel.ULTIMATE: 1048576,
        }
        
        for level, expected_count in expected_counts.items():
            generator = DNAKeyGenerator(level)
            assert generator.segment_count == expected_count


class TestSecurityLayers:
    """Test multi-layer security architecture."""
    
    def test_security_layer_enum_exists(self):
        """Test SecurityLayer enum is defined."""
        assert hasattr(SecurityLayer, 'OUTER_SHELL')
        assert hasattr(SecurityLayer, 'ENTROPY_MATRIX')
        assert hasattr(SecurityLayer, 'SECURITY_FRAMEWORK')
        assert hasattr(SecurityLayer, 'IDENTITY_CORE')
        assert hasattr(SecurityLayer, 'CRYPTO_NUCLEUS')
    
    def test_security_layer_values(self):
        """Test SecurityLayer has correct values (1-5)."""
        assert SecurityLayer.OUTER_SHELL.value == 1
        assert SecurityLayer.ENTROPY_MATRIX.value == 2
        assert SecurityLayer.SECURITY_FRAMEWORK.value == 3
        assert SecurityLayer.IDENTITY_CORE.value == 4
        assert SecurityLayer.CRYPTO_NUCLEUS.value == 5


class TestSecurityMethodsIntegrated:
    """Test security methods tracking."""
    
    def test_security_methods_default_values(self):
        """Test SecurityMethodsIntegrated has default security methods."""
        methods = SecurityMethodsIntegrated()
        
        assert "SHA3-512" in methods.hash_algorithms
        assert "AES-256-GCM" in methods.encryption_algorithms
        assert "Ed25519" in methods.signature_algorithms
        assert "HKDF-SHA512" in methods.key_derivation_functions
    
    def test_security_methods_count(self):
        """Test total methods count is calculated correctly."""
        methods = SecurityMethodsIntegrated()
        
        # Should have 30+ security methods total
        assert methods.total_methods_count >= 30
    
    def test_security_methods_to_dict(self):
        """Test SecurityMethodsIntegrated can be converted to dict."""
        methods = SecurityMethodsIntegrated()
        methods_dict = methods.to_dict()
        
        assert "hash_algorithms" in methods_dict
        assert "encryption_algorithms" in methods_dict
        assert "total_methods_count" in methods_dict


class TestLayerChecksums:
    """Test layer checksum functionality."""
    
    def test_layer_checksum_creation(self):
        """Test LayerChecksum dataclass works correctly."""
        checksum = LayerChecksum(
            layer=1,
            algorithm="SHA3-512",
            checksum="abc123",
            segment_count=100
        )
        
        assert checksum.layer == 1
        assert checksum.algorithm == "SHA3-512"
        assert checksum.checksum == "abc123"
        assert checksum.segment_count == 100
    
    def test_generated_key_has_layer_checksums(self):
        """Test generated keys have layer checksums."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        assert len(key.layer_checksums) > 0
        assert all(isinstance(lc, LayerChecksum) for lc in key.layer_checksums)


class TestExtendedSegmentTypes:
    """Test extended segment types."""
    
    def test_new_segment_types_exist(self):
        """Test new segment types are defined."""
        # Original types
        assert hasattr(SegmentType, 'ENTROPY')
        assert hasattr(SegmentType, 'POLICY')
        assert hasattr(SegmentType, 'HASH')
        
        # New extended types
        assert hasattr(SegmentType, 'KEY_DERIVATION')
        assert hasattr(SegmentType, 'ENCRYPTION')
        assert hasattr(SegmentType, 'NONCE')
        assert hasattr(SegmentType, 'CHALLENGE')
        assert hasattr(SegmentType, 'ATTESTATION')
        assert hasattr(SegmentType, 'FINGERPRINT')
        assert hasattr(SegmentType, 'RECOVERY')
        assert hasattr(SegmentType, 'AUDIT')
        assert hasattr(SegmentType, 'QUANTUM')
        assert hasattr(SegmentType, 'CUSTOM')
    
    def test_segment_type_values(self):
        """Test segment type values are single characters."""
        for seg_type in SegmentType:
            assert len(seg_type.value) == 1


class TestSecurityScore:
    """Test security score calculation."""
    
    def test_security_score_calculated(self):
        """Test security score is calculated for generated keys."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        assert key.security_score > 0
        assert key.security_score <= 100
    
    def test_higher_security_level_higher_score(self):
        """Test that higher security levels produce higher scores."""
        gen_standard = DNAKeyGenerator(SecurityLevel.STANDARD)
        gen_enhanced = DNAKeyGenerator(SecurityLevel.ENHANCED)
        
        key_standard = gen_standard.generate("user@example.com")
        key_enhanced = gen_enhanced.generate("user@example.com")
        
        # Enhanced should have higher or equal score
        assert key_enhanced.security_score >= key_standard.security_score


class TestTotalLines:
    """Test total lines calculation."""
    
    def test_total_lines_calculated(self):
        """Test total lines is calculated for generated keys."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        assert key.total_lines > 0
    
    def test_total_lines_increases_with_security_level(self):
        """Test total lines increases with security level."""
        gen_standard = DNAKeyGenerator(SecurityLevel.STANDARD)
        gen_enhanced = DNAKeyGenerator(SecurityLevel.ENHANCED)
        
        key_standard = gen_standard.generate("user@example.com")
        key_enhanced = gen_enhanced.generate("user@example.com")
        
        assert key_enhanced.total_lines > key_standard.total_lines
