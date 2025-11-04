"""
DNA-Key Authentication System - Revocation Service

Implements DNA key revocation with Certificate Revocation List (CRL).
Handles immediate key revocation and revocation verification.

Revocation Reasons:
- KEY_COMPROMISE: Private key compromised
- AFFILIATION_CHANGED: User left organization
- SUPERSEDED: Key replaced with newer one
- CESSATION_OF_OPERATION: Service discontinued
- PRIVILEGE_WITHDRAWN: Access privileges revoked
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set


class RevocationReason(Enum):
    """Reasons for key revocation."""

    KEY_COMPROMISE = "key_compromise"
    AFFILIATION_CHANGED = "affiliation_changed"
    SUPERSEDED = "superseded"
    CESSATION_OF_OPERATION = "cessation_of_operation"
    PRIVILEGE_WITHDRAWN = "privilege_withdrawn"
    UNSPECIFIED = "unspecified"


@dataclass
class RevocationEntry:
    """Entry in the revocation list."""

    key_id: str
    revoked_at: datetime
    reason: RevocationReason
    revoked_by: str
    notes: Optional[str] = None


@dataclass
class RevocationRequest:
    """Request to revoke a DNA key."""

    key_id: str
    reason: RevocationReason
    revoked_by: str
    notes: Optional[str] = None


@dataclass
class RevocationResponse:
    """Response from revocation operation."""

    success: bool
    key_id: Optional[str] = None
    revoked_at: Optional[datetime] = None
    error_message: Optional[str] = None


class RevocationService:
    """
    Service for revoking DNA keys.

    Maintains a Certificate Revocation List (CRL) and provides
    fast revocation checking for authentication.
    """

    def __init__(self):
        """Initialize revocation service."""
        # Revocation list (key_id -> RevocationEntry)
        # In production, this would be in database
        self._revoked_keys: Dict[str, RevocationEntry] = {}

        # Fast lookup set for O(1) revocation checks
        self._revoked_key_ids: Set[str] = set()

        # CRL version number (incremented on each change)
        self._crl_version = 0

        # Last update timestamp
        self._last_updated = datetime.now(timezone.utc)

    def revoke_key(self, request: RevocationRequest) -> RevocationResponse:
        """
        Revoke a DNA key.

        Args:
            request: Revocation request

        Returns:
            RevocationResponse indicating success or failure

        Example:
            >>> service = RevocationService()
            >>> request = RevocationRequest(
            ...     key_id="dna-abc123",
            ...     reason=RevocationReason.KEY_COMPROMISE,
            ...     revoked_by="admin@example.com",
            ...     notes="Suspected compromise"
            ... )
            >>> response = service.revoke_key(request)
        """
        try:
            # Check if already revoked
            if request.key_id in self._revoked_key_ids:
                return RevocationResponse(success=False, error_message="Key already revoked")

            # Create revocation entry
            revoked_at = datetime.now(timezone.utc)
            entry = RevocationEntry(
                key_id=request.key_id,
                revoked_at=revoked_at,
                reason=request.reason,
                revoked_by=request.revoked_by,
                notes=request.notes,
            )

            # Add to revocation list
            self._revoked_keys[request.key_id] = entry
            self._revoked_key_ids.add(request.key_id)

            # Update CRL metadata
            self._crl_version += 1
            self._last_updated = revoked_at

            return RevocationResponse(success=True, key_id=request.key_id, revoked_at=revoked_at)

        except Exception as e:
            return RevocationResponse(success=False, error_message=str(e))

    def is_revoked(self, key_id: str) -> bool:
        """
        Check if a key is revoked.

        Args:
            key_id: Key ID to check

        Returns:
            True if revoked, False otherwise

        Example:
            >>> if service.is_revoked("dna-abc123"):
            ...     print("Key is revoked")
        """
        return key_id in self._revoked_key_ids

    def get_revocation_entry(self, key_id: str) -> Optional[RevocationEntry]:
        """
        Get revocation details for a key.

        Args:
            key_id: Key ID to look up

        Returns:
            RevocationEntry if revoked, None otherwise
        """
        return self._revoked_keys.get(key_id)

    def get_revocation_list(self) -> List[RevocationEntry]:
        """
        Get complete revocation list.

        Returns:
            List of all revocation entries
        """
        return list(self._revoked_keys.values())

    def get_revoked_count(self) -> int:
        """Get count of revoked keys."""
        return len(self._revoked_key_ids)

    def get_crl_version(self) -> int:
        """Get CRL version number."""
        return self._crl_version

    def get_crl_hash(self) -> str:
        """
        Get cryptographic hash of CRL for integrity verification.

        Returns:
            SHA3-512 hash of the CRL
        """
        hasher = hashlib.sha3_512()

        # Sort entries for deterministic hash
        sorted_entries = sorted(self._revoked_keys.items(), key=lambda x: x[0])

        for key_id, entry in sorted_entries:
            hasher.update(key_id.encode())
            hasher.update(entry.revoked_at.isoformat().encode())
            hasher.update(entry.reason.value.encode())
            hasher.update(entry.revoked_by.encode())

        return hasher.hexdigest()

    def get_crl_info(self) -> Dict[str, any]:
        """
        Get CRL metadata information.

        Returns:
            Dictionary with CRL metadata
        """
        return {
            "version": self._crl_version,
            "last_updated": self._last_updated.isoformat(),
            "total_revoked": self.get_revoked_count(),
            "crl_hash": self.get_crl_hash(),
        }

    def bulk_revoke_keys(
        self, key_ids: List[str], reason: RevocationReason, revoked_by: str, notes: Optional[str] = None
    ) -> Dict[str, RevocationResponse]:
        """
        Revoke multiple keys at once.

        Args:
            key_ids: List of key IDs to revoke
            reason: Revocation reason
            revoked_by: Who is revoking the keys
            notes: Optional notes

        Returns:
            Dictionary mapping key_id to RevocationResponse

        Example:
            >>> results = service.bulk_revoke_keys(
            ...     ["key1", "key2", "key3"],
            ...     RevocationReason.AFFILIATION_CHANGED,
            ...     "admin@example.com",
            ...     "User left organization"
            ... )
        """
        results = {}

        for key_id in key_ids:
            request = RevocationRequest(key_id=key_id, reason=reason, revoked_by=revoked_by, notes=notes)
            results[key_id] = self.revoke_key(request)

        return results

    def get_revocations_by_reason(self, reason: RevocationReason) -> List[RevocationEntry]:
        """
        Get all revocations for a specific reason.

        Args:
            reason: Revocation reason to filter by

        Returns:
            List of matching revocation entries
        """
        return [entry for entry in self._revoked_keys.values() if entry.reason == reason]

    def get_recent_revocations(self, hours: int = 24) -> List[RevocationEntry]:
        """
        Get revocations from the last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent revocation entries
        """
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        return [entry for entry in self._revoked_keys.values() if entry.revoked_at >= cutoff]


def revoke_key(
    key_id: str,
    reason: RevocationReason = RevocationReason.UNSPECIFIED,
    revoked_by: str = "system",
    notes: Optional[str] = None,
) -> RevocationResponse:
    """
    Convenience function to revoke a key.

    Args:
        key_id: Key ID to revoke
        reason: Revocation reason
        revoked_by: Who is revoking
        notes: Optional notes

    Returns:
        RevocationResponse

    Example:
        >>> from server.core.revocation import revoke_key, RevocationReason
        >>> response = revoke_key("dna-abc123", RevocationReason.KEY_COMPROMISE)
    """
    service = RevocationService()
    request = RevocationRequest(key_id=key_id, reason=reason, revoked_by=revoked_by, notes=notes)
    return service.revoke_key(request)
