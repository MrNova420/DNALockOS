"""
DNA-Key Authentication System - Security Techniques Tests

Tests for the security techniques catalog.
"""

import pytest

from server.crypto.security_techniques import (
    SecurityCategory,
    SecurityTechnique,
    ALL_SECURITY_TECHNIQUES,
    CRYPTOGRAPHIC_TECHNIQUES,
    KEY_MANAGEMENT_TECHNIQUES,
    AUTHENTICATION_TECHNIQUES,
    ANTI_ATTACK_TECHNIQUES,
    PRIVACY_TECHNIQUES,
    AUDIT_TECHNIQUES,
    RESILIENCE_TECHNIQUES,
    get_all_techniques,
    get_techniques_by_category,
    get_implemented_techniques,
    get_technique_count,
    generate_security_report,
)


class TestSecurityTechniquesCatalog:
    """Test the security techniques catalog."""
    
    def test_total_techniques_count(self):
        """Test that we have a significant number of techniques."""
        techniques = get_all_techniques()
        
        # We should have 70+ techniques defined
        assert len(techniques) >= 70
    
    def test_techniques_have_required_fields(self):
        """Test that all techniques have required fields."""
        for technique in ALL_SECURITY_TECHNIQUES:
            assert technique.id is not None
            assert technique.name is not None
            assert technique.category is not None
            assert technique.description is not None
            assert 1 <= technique.strength_level <= 10
            assert technique.implementation_status in ["implemented", "planned", "research"]
    
    def test_technique_ids_unique(self):
        """Test that technique IDs are unique."""
        ids = [t.id for t in ALL_SECURITY_TECHNIQUES]
        assert len(ids) == len(set(ids))
    
    def test_cryptographic_techniques_exist(self):
        """Test that cryptographic techniques are defined."""
        assert len(CRYPTOGRAPHIC_TECHNIQUES) >= 25
        
        # Check for specific important techniques
        technique_names = [t.name for t in CRYPTOGRAPHIC_TECHNIQUES]
        assert any("SHA3" in name for name in technique_names)
        assert any("Ed25519" in name for name in technique_names)
        assert any("AES" in name for name in technique_names)
    
    def test_key_management_techniques_exist(self):
        """Test that key management techniques are defined."""
        assert len(KEY_MANAGEMENT_TECHNIQUES) >= 10
    
    def test_authentication_techniques_exist(self):
        """Test that authentication techniques are defined."""
        assert len(AUTHENTICATION_TECHNIQUES) >= 10
        
        # Check for DNA-specific authentication
        technique_names = [t.name for t in AUTHENTICATION_TECHNIQUES]
        assert any("DNA" in name for name in technique_names)
    
    def test_anti_attack_techniques_exist(self):
        """Test that anti-attack techniques are defined."""
        assert len(ANTI_ATTACK_TECHNIQUES) >= 10
        
        # Check for specific protections
        technique_names = [t.name for t in ANTI_ATTACK_TECHNIQUES]
        assert any("Brute Force" in name for name in technique_names)
        assert any("Rate Limiting" in name for name in technique_names)
    
    def test_privacy_techniques_exist(self):
        """Test that privacy techniques are defined."""
        assert len(PRIVACY_TECHNIQUES) >= 10
    
    def test_audit_techniques_exist(self):
        """Test that audit techniques are defined."""
        assert len(AUDIT_TECHNIQUES) >= 5
    
    def test_resilience_techniques_exist(self):
        """Test that resilience techniques are defined."""
        assert len(RESILIENCE_TECHNIQUES) >= 5


class TestSecurityCategory:
    """Test security categories."""
    
    def test_all_categories_exist(self):
        """Test that all expected categories exist."""
        expected_categories = [
            SecurityCategory.CRYPTOGRAPHIC,
            SecurityCategory.KEY_MANAGEMENT,
            SecurityCategory.AUTHENTICATION,
            SecurityCategory.ANTI_ATTACK,
            SecurityCategory.PRIVACY,
            SecurityCategory.AUDIT,
            SecurityCategory.RESILIENCE
        ]
        
        for category in expected_categories:
            techniques = get_techniques_by_category(category)
            assert len(techniques) > 0


class TestGetTechniquesByCategory:
    """Test filtering techniques by category."""
    
    def test_get_cryptographic(self):
        """Test getting cryptographic techniques."""
        techniques = get_techniques_by_category(SecurityCategory.CRYPTOGRAPHIC)
        
        assert len(techniques) > 0
        assert all(t.category == SecurityCategory.CRYPTOGRAPHIC for t in techniques)
    
    def test_get_authentication(self):
        """Test getting authentication techniques."""
        techniques = get_techniques_by_category(SecurityCategory.AUTHENTICATION)
        
        assert len(techniques) > 0
        assert all(t.category == SecurityCategory.AUTHENTICATION for t in techniques)


class TestGetImplementedTechniques:
    """Test filtering implemented techniques."""
    
    def test_implemented_techniques_count(self):
        """Test that most techniques are implemented."""
        implemented = get_implemented_techniques()
        all_techniques = get_all_techniques()
        
        # At least 60% should be implemented
        assert len(implemented) >= len(all_techniques) * 0.6
    
    def test_implemented_techniques_status(self):
        """Test that filtered techniques have correct status."""
        implemented = get_implemented_techniques()
        
        for technique in implemented:
            assert technique.implementation_status == "implemented"


class TestTechniqueCount:
    """Test technique counting."""
    
    def test_count_totals(self):
        """Test total counts."""
        counts = get_technique_count()
        
        assert counts["total"] == len(ALL_SECURITY_TECHNIQUES)
        assert counts["implemented"] + counts["planned"] <= counts["total"]
    
    def test_count_by_category(self):
        """Test counts by category."""
        counts = get_technique_count()
        
        assert "by_category" in counts
        assert len(counts["by_category"]) == len(SecurityCategory)


class TestSecurityReport:
    """Test security report generation."""
    
    def test_generate_report(self):
        """Test generating a security report."""
        report = generate_security_report()
        
        assert "report_generated" in report
        assert "total_techniques" in report
        assert "implemented_techniques" in report
        assert "categories" in report
        assert "average_strength" in report
        assert "compliance_references" in report
    
    def test_report_has_all_categories(self):
        """Test that report includes all categories."""
        report = generate_security_report()
        
        for category in SecurityCategory:
            assert category.value in report["categories"]
    
    def test_report_average_strength(self):
        """Test average strength calculation."""
        report = generate_security_report()
        
        # Average should be between 1 and 10
        assert 1 <= report["average_strength"] <= 10
        
        # Should be high for our security-focused system
        assert report["average_strength"] >= 8
    
    def test_report_compliance_references(self):
        """Test compliance references are collected."""
        report = generate_security_report()
        
        references = report["compliance_references"]
        
        assert len(references) > 0
        # Check for important standards
        assert any("FIPS" in ref for ref in references)
        assert any("NIST" in ref or "RFC" in ref for ref in references)


class TestSecurityTechniqueStrength:
    """Test security technique strength levels."""
    
    def test_strength_levels_valid(self):
        """Test that all strength levels are valid (1-10)."""
        for technique in ALL_SECURITY_TECHNIQUES:
            assert 1 <= technique.strength_level <= 10
    
    def test_critical_techniques_high_strength(self):
        """Test that critical techniques have high strength."""
        critical_ids = ["CRYPTO-001", "CRYPTO-005", "CRYPTO-008", "AUTH-001"]
        
        for technique in ALL_SECURITY_TECHNIQUES:
            if technique.id in critical_ids:
                assert technique.strength_level >= 9


class TestSecurityTechniqueReferences:
    """Test security technique references."""
    
    def test_techniques_have_references(self):
        """Test that techniques have references."""
        for technique in ALL_SECURITY_TECHNIQUES:
            assert len(technique.references) >= 1
    
    def test_references_are_valid_strings(self):
        """Test that references are valid strings."""
        for technique in ALL_SECURITY_TECHNIQUES:
            for ref in technique.references:
                assert isinstance(ref, str)
                assert len(ref) > 0
