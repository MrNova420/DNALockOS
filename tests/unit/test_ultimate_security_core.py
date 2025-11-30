"""
DNA-Key Authentication System - Ultimate Security Core Tests

Comprehensive tests for the ultimate security core components.
"""

import pytest
from datetime import datetime, timezone

from server.crypto.ultimate_security_core import (
    SecurityClassification,
    ThreatLevel,
    ComplianceFramework,
    CryptoAlgorithmSuite,
    CryptoParameters,
    HardwareSecurityType,
    HardwareBinding,
    BiometricType,
    BiometricSecurityLevel,
    BiometricTemplate,
    VerificationBarrierResult,
    BarrierResult,
    UltimateVerificationEngine,
    UltimateDNAStrandConfig,
    generate_ultimate_security_hash,
)


class TestSecurityClassification:
    """Tests for security classification enum."""
    
    def test_classification_levels(self):
        """Test all classification levels exist."""
        assert SecurityClassification.UNCLASSIFIED.value == "UNCLASSIFIED"
        assert SecurityClassification.SECRET.value == "SECRET"
        assert SecurityClassification.TOP_SECRET.value == "TOP_SECRET"
        assert SecurityClassification.ULTIMATE_CLEARANCE.value == "ULTIMATE_CLEARANCE"
    
    def test_special_compartments(self):
        """Test special compartment classifications."""
        assert SecurityClassification.TOP_SECRET_SCI.value == "TOP_SECRET_SCI"
        assert SecurityClassification.SAP.value == "SAP"


class TestThreatLevel:
    """Tests for threat level enum."""
    
    def test_threat_levels(self):
        """Test threat level values."""
        assert ThreatLevel.GREEN.value == 1
        assert ThreatLevel.YELLOW.value == 3
        assert ThreatLevel.RED.value == 5
    
    def test_threat_level_ordering(self):
        """Test that threat levels are ordered correctly."""
        assert ThreatLevel.GREEN.value < ThreatLevel.BLUE.value
        assert ThreatLevel.BLUE.value < ThreatLevel.YELLOW.value
        assert ThreatLevel.YELLOW.value < ThreatLevel.ORANGE.value
        assert ThreatLevel.ORANGE.value < ThreatLevel.RED.value


class TestComplianceFramework:
    """Tests for compliance framework flags."""
    
    def test_individual_frameworks(self):
        """Test individual compliance frameworks."""
        assert ComplianceFramework.FIPS_140_3 != 0
        assert ComplianceFramework.NIST_800_53 != 0
        assert ComplianceFramework.SOC_2 != 0
        assert ComplianceFramework.HIPAA != 0
    
    def test_combined_frameworks(self):
        """Test combined framework presets."""
        # STANDARD includes FIPS, NIST, SOC2
        assert (ComplianceFramework.STANDARD & ComplianceFramework.FIPS_140_3) != 0
        assert (ComplianceFramework.STANDARD & ComplianceFramework.SOC_2) != 0
        
        # MILITARY includes everything
        assert (ComplianceFramework.MILITARY & ComplianceFramework.GOVERNMENT) == ComplianceFramework.GOVERNMENT
    
    def test_ultimate_compliance(self):
        """Test ultimate compliance includes everything."""
        ultimate = ComplianceFramework.ULTIMATE
        
        # Should include all major frameworks
        assert (ultimate & ComplianceFramework.FIPS_140_3) != 0
        assert (ultimate & ComplianceFramework.DoD_IL6) != 0
        assert (ultimate & ComplianceFramework.ITAR) != 0


class TestCryptoAlgorithmSuite:
    """Tests for crypto algorithm suites."""
    
    def test_suite_values(self):
        """Test suite enum values."""
        assert CryptoAlgorithmSuite.STANDARD.value == "standard"
        assert CryptoAlgorithmSuite.ULTIMATE.value == "ultimate"
        assert CryptoAlgorithmSuite.HYBRID_PQ.value == "hybrid_pq"
    
    def test_crypto_parameters_for_suite(self):
        """Test getting parameters for suites."""
        params = CryptoParameters.for_suite(CryptoAlgorithmSuite.ULTIMATE)
        
        assert params.primary_hash == "SHA3-512"
        assert params.pq_signature == "Dilithium5"
        assert params.min_entropy_bits == 1024
    
    def test_cnsa_parameters(self):
        """Test CNSA 2.0 parameters."""
        params = CryptoParameters.for_suite(CryptoAlgorithmSuite.CNSA_2_0)
        
        assert params.primary_hash == "SHA-384"
        assert params.asymmetric_key_size == 384


class TestHardwareSecurityType:
    """Tests for hardware security types."""
    
    def test_consumer_devices(self):
        """Test consumer device hardware types."""
        assert HardwareSecurityType.APPLE_SECURE_ENCLAVE.value == "apple_secure_enclave"
        assert HardwareSecurityType.ANDROID_STRONGBOX.value == "android_strongbox"
        assert HardwareSecurityType.WINDOWS_TPM.value == "windows_tpm"
    
    def test_enterprise_hsms(self):
        """Test enterprise HSM types."""
        assert HardwareSecurityType.HSM_FIPS_140_3_L3.value == "hsm_fips_140_3_l3"
        assert HardwareSecurityType.HSM_FIPS_140_3_L4.value == "hsm_fips_140_3_l4"
    
    def test_hardware_keys(self):
        """Test hardware key types."""
        assert HardwareSecurityType.YUBIKEY.value == "yubikey"
        assert HardwareSecurityType.TITAN_KEY.value == "titan_key"


class TestBiometricTypes:
    """Tests for biometric types and levels."""
    
    def test_biometric_types(self):
        """Test biometric type enum."""
        assert BiometricType.FACE.value == "face"
        assert BiometricType.FINGERPRINT.value == "fingerprint"
        assert BiometricType.MULTIMODAL.value == "multimodal"
    
    def test_biometric_security_levels(self):
        """Test biometric security levels."""
        assert BiometricSecurityLevel.BASIC.value == 1
        assert BiometricSecurityLevel.ULTIMATE.value == 5
    
    def test_biometric_template_creation(self):
        """Test creating a biometric template."""
        template = BiometricTemplate(
            biometric_type=BiometricType.FACE,
            security_level=BiometricSecurityLevel.MAXIMUM,
            template_hash=b"hash123",
            fuzzy_commitment=b"commit456",
            helper_data=b"helper789"
        )
        
        assert template.biometric_type == BiometricType.FACE
        assert template.liveness_required is True
        assert template.presentation_attack_detection is True


class TestUltimateVerificationEngine:
    """Tests for the 24-barrier verification engine."""
    
    def test_create_engine(self):
        """Test creating verification engine."""
        engine = UltimateVerificationEngine()
        
        assert engine.threat_level == ThreatLevel.GREEN
    
    def test_create_engine_with_threat_level(self):
        """Test creating engine with custom threat level."""
        engine = UltimateVerificationEngine(threat_level=ThreatLevel.RED)
        
        assert engine.threat_level == ThreatLevel.RED
    
    def test_barriers_count(self):
        """Test that 24 barriers are defined."""
        assert len(UltimateVerificationEngine.BARRIERS) == 24
    
    def test_barrier_ids_sequential(self):
        """Test barrier IDs are sequential 1-24."""
        ids = [b[0] for b in UltimateVerificationEngine.BARRIERS]
        
        assert ids == list(range(1, 25))
    
    def test_barrier_result_enum(self):
        """Test verification barrier result enum."""
        assert VerificationBarrierResult.PASSED.value == "passed"
        assert VerificationBarrierResult.FAILED.value == "failed"
        assert VerificationBarrierResult.WARNING.value == "warning"


class TestUltimateDNAStrandConfig:
    """Tests for DNA strand configuration."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = UltimateDNAStrandConfig()
        
        assert config.segment_count == 1048576  # 1 million
        assert config.require_hardware_binding is True
        assert config.require_biometric is True
        assert config.require_mfa is True
    
    def test_ultimate_classification(self):
        """Test ultimate security configuration."""
        config = UltimateDNAStrandConfig(
            classification=SecurityClassification.ULTIMATE_CLEARANCE,
            compliance=ComplianceFramework.ULTIMATE,
            crypto_suite=CryptoAlgorithmSuite.ULTIMATE
        )
        
        assert config.classification == SecurityClassification.ULTIMATE_CLEARANCE
        assert config.enable_pq_crypto is True


class TestGenerateUltimateSecurityHash:
    """Tests for ultimate security hash generation."""
    
    def test_generate_hash(self):
        """Test generating ultimate security hash."""
        hash_value = generate_ultimate_security_hash()
        
        # SHA3-512 hex output = 128 characters
        assert len(hash_value) == 128
    
    def test_hashes_are_unique(self):
        """Test that generated hashes are unique."""
        hashes = [generate_ultimate_security_hash() for _ in range(10)]
        
        # All should be unique
        assert len(set(hashes)) == 10
    
    def test_hash_is_hex(self):
        """Test that hash is valid hex."""
        hash_value = generate_ultimate_security_hash()
        
        # Should be valid hex
        int(hash_value, 16)  # Will raise if not valid hex


class TestBarrierResult:
    """Tests for barrier result dataclass."""
    
    def test_create_barrier_result(self):
        """Test creating a barrier result."""
        result = BarrierResult(
            barrier_id=1,
            barrier_name="Rate Limiting",
            result=VerificationBarrierResult.PASSED,
            details="Within rate limit",
            execution_time_ms=5.5,
            risk_contribution=0.0
        )
        
        assert result.barrier_id == 1
        assert result.result == VerificationBarrierResult.PASSED
        assert result.execution_time_ms == 5.5


class TestHardwareBinding:
    """Tests for hardware binding."""
    
    def test_create_hardware_binding(self):
        """Test creating hardware binding."""
        binding = HardwareBinding(
            hardware_type=HardwareSecurityType.APPLE_SECURE_ENCLAVE,
            device_id="device123",
            attestation_certificate=b"cert_data",
            binding_timestamp=datetime.now(timezone.utc),
            binding_signature=b"signature"
        )
        
        assert binding.hardware_type == HardwareSecurityType.APPLE_SECURE_ENCLAVE
        assert binding.device_id == "device123"
    
    def test_verify_attestation(self):
        """Test attestation verification."""
        binding = HardwareBinding(
            hardware_type=HardwareSecurityType.WINDOWS_TPM,
            device_id="device456",
            attestation_certificate=b"valid_cert",
            binding_timestamp=datetime.now(timezone.utc),
            binding_signature=b"sig"
        )
        
        # With non-empty cert, should return True (simplified)
        assert binding.verify_attestation() is True
    
    def test_empty_attestation_fails(self):
        """Test that empty attestation fails."""
        binding = HardwareBinding(
            hardware_type=HardwareSecurityType.SOFTWARE_ONLY,
            device_id="device789",
            attestation_certificate=b"",
            binding_timestamp=datetime.now(timezone.utc),
            binding_signature=b""
        )
        
        assert binding.verify_attestation() is False
