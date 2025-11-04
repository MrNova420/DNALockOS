"""
DNA-Key Authentication System - CBOR Serialization

Implements canonical CBOR serialization for DNA keys.
CBOR (Concise Binary Object Representation) provides:
- Compact binary encoding (50% smaller than JSON)
- Deterministic encoding for signatures
- Fast serialization/deserialization
- Schema-free data interchange

Reference: RFC 8949 - Concise Binary Object Representation (CBOR)
"""

from datetime import datetime
from typing import Any, Dict

import cbor2

from server.crypto.dna_key import DNAKey, DNASegment, SegmentType


class DNAKeySerializer:
    """
    CBOR serializer for DNA keys.

    Provides deterministic serialization suitable for signing
    and compact storage/transmission.
    """

    @staticmethod
    def serialize(dna_key: DNAKey) -> bytes:
        """
        Serialize DNA key to canonical CBOR format.

        Args:
            dna_key: DNA key to serialize

        Returns:
            CBOR-encoded bytes

        Example:
            >>> from server.crypto.dna_generator import generate_dna_key, SecurityLevel
            >>> from server.crypto.serialization import DNAKeySerializer
            >>> key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
            >>> cbor_data = DNAKeySerializer.serialize(key)
            >>> print(f"Serialized to {len(cbor_data)} bytes")
        """
        # Convert to dictionary representation
        key_dict = dna_key.to_dict()

        # Encode to CBOR with canonical encoding
        cbor_data = cbor2.dumps(key_dict, canonical=True)

        return cbor_data

    @staticmethod
    def deserialize(cbor_data: bytes) -> DNAKey:
        """
        Deserialize DNA key from CBOR format.

        Args:
            cbor_data: CBOR-encoded bytes

        Returns:
            DNAKey object

        Raises:
            ValueError: If CBOR data is invalid or incomplete

        Example:
            >>> cbor_data = DNAKeySerializer.serialize(key)
            >>> restored_key = DNAKeySerializer.deserialize(cbor_data)
            >>> assert restored_key.key_id == key.key_id
        """
        # Decode CBOR
        key_dict = cbor2.loads(cbor_data)

        # Reconstruct DNA key from dictionary
        return DNAKeySerializer._dict_to_dna_key(key_dict)

    @staticmethod
    def _dict_to_dna_key(data: Dict[str, Any]) -> DNAKey:
        """
        Reconstruct DNAKey from dictionary.

        Args:
            data: Dictionary representation of DNA key

        Returns:
            DNAKey object
        """
        from server.crypto.dna_key import (
            CryptographicMaterial,
            DNAHelix,
            IssuerInfo,
            PolicyBinding,
            SubjectInfo,
            VisualDNA,
        )

        # Parse timestamps
        created = datetime.fromisoformat(data["created_timestamp"]) if data.get("created_timestamp") else None
        expires = datetime.fromisoformat(data["expires_timestamp"]) if data.get("expires_timestamp") else None

        # Reconstruct issuer info
        issuer = None
        if data.get("issuer"):
            issuer_data = data["issuer"]
            issuer = IssuerInfo(
                organization_id=issuer_data["organization_id"],
                issuer_public_key=bytes.fromhex(issuer_data["issuer_public_key"]),
                issuer_signature=bytes.fromhex(issuer_data["issuer_signature"])
                if issuer_data.get("issuer_signature")
                else None,
            )

        # Reconstruct subject info
        subject = None
        if data.get("subject"):
            subject_data = data["subject"]
            subject = SubjectInfo(
                subject_id=subject_data["subject_id"],
                subject_type=subject_data["subject_type"],
                attributes_hash=subject_data["attributes_hash"],
            )

        # Reconstruct DNA helix
        helix_data = data["dna_helix"]
        segments = []
        for seg_data in helix_data["segments"]:
            segment = DNASegment(
                position=seg_data["position"],
                type=SegmentType(seg_data["type"]),
                data=bytes.fromhex(seg_data["data"]),
                segment_hash=seg_data.get("segment_hash"),
            )
            segments.append(segment)

        helix = DNAHelix(segments=segments)
        helix.checksum = helix_data.get("checksum")

        # Reconstruct cryptographic material
        crypto_material = None
        if data.get("cryptographic_material"):
            crypto_data = data["cryptographic_material"]
            crypto_material = CryptographicMaterial(
                algorithm=crypto_data["algorithm"],
                public_key=bytes.fromhex(crypto_data["public_key"]) if crypto_data.get("public_key") else None,
                salt=bytes.fromhex(crypto_data["salt"]) if crypto_data.get("salt") else None,
                kdf_info=crypto_data.get("kdf_info", "DNAKeyAuthSystem-v1"),
            )

        # Reconstruct policy binding
        policy = None
        if data.get("policy_binding"):
            policy_data = data["policy_binding"]
            policy = PolicyBinding(
                policy_id=policy_data["policy_id"],
                policy_version=policy_data["policy_version"],
                policy_hash=policy_data["policy_hash"],
                mfa_required=policy_data.get("mfa_required", False),
                biometric_required=policy_data.get("biometric_required", False),
                device_binding_required=policy_data.get("device_binding_required", False),
            )

        # Reconstruct visual DNA
        visual = VisualDNA()
        if data.get("visual_dna"):
            visual_data = data["visual_dna"]
            visual.color_palette = visual_data.get("color_palette", visual.color_palette)
            visual.helix_rotation = visual_data.get("helix_rotation", visual.helix_rotation)
            visual.glow_intensity = visual_data.get("glow_intensity", visual.glow_intensity)
            visual.animation_seed = visual_data.get("animation_seed")

        # Create DNA key
        dna_key = DNAKey(
            format_version=data.get("format_version", "1.0"),
            key_id=data.get("key_id"),
            created_timestamp=created,
            expires_timestamp=expires,
            issuer=issuer,
            subject=subject,
            dna_helix=helix,
            cryptographic_material=crypto_material,
            policy_binding=policy,
            visual_dna=visual,
        )

        return dna_key

    @staticmethod
    def get_serialized_size(dna_key: DNAKey) -> int:
        """
        Get the size of serialized DNA key in bytes.

        Args:
            dna_key: DNA key to measure

        Returns:
            Size in bytes
        """
        cbor_data = DNAKeySerializer.serialize(dna_key)
        return len(cbor_data)


def serialize_dna_key(dna_key: DNAKey) -> bytes:
    """
    Convenience function to serialize a DNA key to CBOR.

    Args:
        dna_key: DNA key to serialize

    Returns:
        CBOR-encoded bytes

    Example:
        >>> from server.crypto.serialization import serialize_dna_key, deserialize_dna_key
        >>> cbor_data = serialize_dna_key(key)
        >>> restored = deserialize_dna_key(cbor_data)
    """
    return DNAKeySerializer.serialize(dna_key)


def deserialize_dna_key(cbor_data: bytes) -> DNAKey:
    """
    Convenience function to deserialize a DNA key from CBOR.

    Args:
        cbor_data: CBOR-encoded bytes

    Returns:
        DNAKey object
    """
    return DNAKeySerializer.deserialize(cbor_data)
