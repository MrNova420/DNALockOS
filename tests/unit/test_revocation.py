"""
DNA-Key Authentication System - Revocation Service Tests

Comprehensive test suite for revocation service.
"""

import pytest
from datetime import datetime, timezone, timedelta

from server.core.revocation import (
    RevocationService,
    RevocationRequest,
    RevocationReason,
    revoke_key
)


class TestRevocationService:
    """Test revocation service."""
    
    def test_create_service(self):
        """Test creating revocation service."""
        service = RevocationService()
        
        assert service.get_revoked_count() == 0
        assert service.get_crl_version() == 0
    
    def test_revoke_key(self):
        """Test revoking a key."""
        service = RevocationService()
        request = RevocationRequest(
            key_id="dna-test123",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin@example.com"
        )
        
        response = service.revoke_key(request)
        
        assert response.success is True
        assert response.key_id == "dna-test123"
        assert response.revoked_at is not None
    
    def test_revoked_key_is_detected(self):
        """Test that revoked key is detected."""
        service = RevocationService()
        key_id = "dna-test123"
        
        request = RevocationRequest(
            key_id=key_id,
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin"
        )
        service.revoke_key(request)
        
        assert service.is_revoked(key_id) is True
    
    def test_non_revoked_key_not_detected(self):
        """Test that non-revoked key is not detected as revoked."""
        service = RevocationService()
        
        assert service.is_revoked("non-existent-key") is False
    
    def test_cannot_revoke_twice(self):
        """Test that key cannot be revoked twice."""
        service = RevocationService()
        request = RevocationRequest(
            key_id="dna-test123",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin"
        )
        
        response1 = service.revoke_key(request)
        response2 = service.revoke_key(request)
        
        assert response1.success is True
        assert response2.success is False
        assert "already revoked" in response2.error_message


class TestRevocationEntry:
    """Test revocation entry retrieval."""
    
    def test_get_revocation_entry(self):
        """Test getting revocation entry details."""
        service = RevocationService()
        request = RevocationRequest(
            key_id="dna-test123",
            reason=RevocationReason.AFFILIATION_CHANGED,
            revoked_by="hr@example.com",
            notes="User left company"
        )
        service.revoke_key(request)
        
        entry = service.get_revocation_entry("dna-test123")
        
        assert entry is not None
        assert entry.key_id == "dna-test123"
        assert entry.reason == RevocationReason.AFFILIATION_CHANGED
        assert entry.revoked_by == "hr@example.com"
        assert entry.notes == "User left company"
    
    def test_get_nonexistent_entry(self):
        """Test getting nonexistent entry returns None."""
        service = RevocationService()
        
        entry = service.get_revocation_entry("nonexistent")
        
        assert entry is None


class TestRevocationList:
    """Test revocation list operations."""
    
    def test_get_revocation_list(self):
        """Test getting complete revocation list."""
        service = RevocationService()
        
        # Revoke multiple keys
        for i in range(3):
            request = RevocationRequest(
                key_id=f"dna-key{i}",
                reason=RevocationReason.KEY_COMPROMISE,
                revoked_by="admin"
            )
            service.revoke_key(request)
        
        revocation_list = service.get_revocation_list()
        
        assert len(revocation_list) == 3
    
    def test_revoked_count(self):
        """Test getting count of revoked keys."""
        service = RevocationService()
        
        assert service.get_revoked_count() == 0
        
        service.revoke_key(RevocationRequest(
            key_id="key1",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin"
        ))
        
        assert service.get_revoked_count() == 1


class TestCRLMetadata:
    """Test CRL metadata."""
    
    def test_crl_version_increments(self):
        """Test that CRL version increments on revocation."""
        service = RevocationService()
        
        initial_version = service.get_crl_version()
        
        service.revoke_key(RevocationRequest(
            key_id="key1",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin"
        ))
        
        assert service.get_crl_version() == initial_version + 1
    
    def test_crl_hash(self):
        """Test CRL hash generation."""
        service = RevocationService()
        
        service.revoke_key(RevocationRequest(
            key_id="key1",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin"
        ))
        
        crl_hash = service.get_crl_hash()
        
        assert isinstance(crl_hash, str)
        assert len(crl_hash) == 128  # SHA3-512 hex
    
    def test_crl_hash_deterministic(self):
        """Test that CRL hash is deterministic."""
        service = RevocationService()
        
        service.revoke_key(RevocationRequest(
            key_id="key1",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin"
        ))
        
        hash1 = service.get_crl_hash()
        hash2 = service.get_crl_hash()
        
        assert hash1 == hash2
    
    def test_crl_info(self):
        """Test getting CRL info."""
        service = RevocationService()
        
        service.revoke_key(RevocationRequest(
            key_id="key1",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin"
        ))
        
        info = service.get_crl_info()
        
        assert "version" in info
        assert "last_updated" in info
        assert "total_revoked" in info
        assert "crl_hash" in info
        assert info["total_revoked"] == 1


class TestBulkRevocation:
    """Test bulk revocation operations."""
    
    def test_bulk_revoke_keys(self):
        """Test bulk revoking multiple keys."""
        service = RevocationService()
        key_ids = ["key1", "key2", "key3"]
        
        results = service.bulk_revoke_keys(
            key_ids,
            RevocationReason.AFFILIATION_CHANGED,
            "admin",
            "Batch revocation"
        )
        
        assert len(results) == 3
        assert all(r.success for r in results.values())
        assert service.get_revoked_count() == 3


class TestRevocationFiltering:
    """Test revocation filtering and queries."""
    
    def test_get_revocations_by_reason(self):
        """Test filtering revocations by reason."""
        service = RevocationService()
        
        # Revoke with different reasons
        service.revoke_key(RevocationRequest(
            key_id="key1",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin"
        ))
        service.revoke_key(RevocationRequest(
            key_id="key2",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin"
        ))
        service.revoke_key(RevocationRequest(
            key_id="key3",
            reason=RevocationReason.AFFILIATION_CHANGED,
            revoked_by="admin"
        ))
        
        compromised = service.get_revocations_by_reason(RevocationReason.KEY_COMPROMISE)
        
        assert len(compromised) == 2
    
    def test_get_recent_revocations(self):
        """Test getting recent revocations."""
        service = RevocationService()
        
        # Revoke a key
        service.revoke_key(RevocationRequest(
            key_id="key1",
            reason=RevocationReason.KEY_COMPROMISE,
            revoked_by="admin"
        ))
        
        recent = service.get_recent_revocations(hours=24)
        
        assert len(recent) == 1
        assert recent[0].key_id == "key1"


class TestConvenienceFunction:
    """Test convenience function."""
    
    def test_revoke_key_function(self):
        """Test revoke_key convenience function."""
        response = revoke_key("dna-test123", RevocationReason.KEY_COMPROMISE)
        
        # Note: Creates new service instance, so won't persist
        assert response.success is True


class TestRevocationReasons:
    """Test different revocation reasons."""
    
    def test_all_revocation_reasons(self):
        """Test that all revocation reasons work."""
        service = RevocationService()
        
        reasons = [
            RevocationReason.KEY_COMPROMISE,
            RevocationReason.AFFILIATION_CHANGED,
            RevocationReason.SUPERSEDED,
            RevocationReason.CESSATION_OF_OPERATION,
            RevocationReason.PRIVILEGE_WITHDRAWN,
            RevocationReason.UNSPECIFIED
        ]
        
        for i, reason in enumerate(reasons):
            request = RevocationRequest(
                key_id=f"key{i}",
                reason=reason,
                revoked_by="admin"
            )
            response = service.revoke_key(request)
            assert response.success is True
