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
DNA-Key Authentication System - Platform Fallback Tests

Tests for platform-aware event loop, crypto backend fallbacks,
and optional messaging functionality.
"""

import pytest
import sys


class TestEventLoopFallback:
    """Test platform-aware event loop setup."""

    def test_get_platform_info(self):
        """Test platform info retrieval."""
        from server.runtime.event_loop import get_platform_info

        info = get_platform_info()

        assert "platform" in info
        assert "python_version" in info
        assert "python_version_info" in info
        assert "is_android" in info
        assert "is_windows" in info
        assert "uvloop_supported" in info
        assert "uvloop_available" in info

    def test_platform_info_python_version(self):
        """Test Python version info is correct."""
        from server.runtime.event_loop import get_platform_info

        info = get_platform_info()

        assert info["python_version_info"]["major"] == sys.version_info.major
        assert info["python_version_info"]["minor"] == sys.version_info.minor

    def test_install_best_event_loop_returns_string(self):
        """Test event loop installation returns type string."""
        from server.runtime.event_loop import install_best_event_loop

        result = install_best_event_loop()

        assert result in ["uvloop", "asyncio"]

    def test_is_android_detection(self):
        """Test Android detection doesn't crash."""
        from server.runtime.event_loop import is_android

        result = is_android()

        assert isinstance(result, bool)

    def test_is_unsupported_platform(self):
        """Test unsupported platform detection."""
        from server.runtime.event_loop import is_unsupported_platform

        result = is_unsupported_platform()

        assert isinstance(result, bool)


class TestCryptoBackend:
    """Test crypto backend with fallbacks."""

    def test_check_nacl_availability(self):
        """Test PyNaCl availability check."""
        from server.crypto.backend import is_nacl_available

        result = is_nacl_available()

        assert isinstance(result, bool)

    def test_check_cryptography_availability(self):
        """Test cryptography library availability check."""
        from server.crypto.backend import is_cryptography_available

        result = is_cryptography_available()

        assert isinstance(result, bool)

    def test_get_available_backends(self):
        """Test listing available backends."""
        from server.crypto.backend import get_available_backends

        backends = get_available_backends()

        assert isinstance(backends, list)
        # At least one backend should be available
        assert len(backends) > 0

    def test_get_signer_backend(self):
        """Test getting a signer backend."""
        from server.crypto.backend import get_signer_backend

        signer = get_signer_backend()

        assert hasattr(signer, "sign")
        assert hasattr(signer, "verify")
        assert hasattr(signer, "get_public_key")
        assert hasattr(signer, "backend_name")

    def test_signer_sign_and_verify(self):
        """Test signing and verification."""
        from server.crypto.backend import get_signer_backend

        signer = get_signer_backend()
        message = b"Test message for signing"

        signature = signer.sign(message)

        assert isinstance(signature, bytes)
        assert len(signature) == 64

        result = signer.verify(message, signature)
        assert result is True

    def test_signer_verify_wrong_message(self):
        """Test verification fails with wrong message."""
        from server.crypto.backend import get_signer_backend

        signer = get_signer_backend()
        message = b"Original message"
        wrong_message = b"Wrong message"

        signature = signer.sign(message)
        result = signer.verify(wrong_message, signature)

        assert result is False

    def test_signer_deterministic_with_seed(self):
        """Test deterministic key generation with seed."""
        from server.crypto.backend import get_signer_backend

        seed = b"a" * 32
        signer1 = get_signer_backend(seed)
        signer2 = get_signer_backend(seed)

        assert signer1.get_public_key() == signer2.get_public_key()

    def test_generate_keypair(self):
        """Test keypair generation."""
        from server.crypto.backend import generate_keypair

        private_key, public_key = generate_keypair()

        assert isinstance(private_key, bytes)
        assert isinstance(public_key, bytes)
        assert len(private_key) == 32
        assert len(public_key) == 32

    def test_signer_backend_name(self):
        """Test backend name is reported."""
        from server.crypto.backend import get_signer_backend

        signer = get_signer_backend()

        assert signer.backend_name in ["PyNaCl (libsodium)", "cryptography", "disabled"]


class TestZMQClient:
    """Test optional ZMQ messaging."""

    def test_zmq_availability_check(self):
        """Test ZMQ availability check."""
        from server.messaging.zmq_client import is_zmq_available

        result = is_zmq_available()

        assert isinstance(result, bool)

    def test_create_zmq_client(self):
        """Test creating ZMQ client."""
        from server.messaging.zmq_client import create_zmq_client

        client = create_zmq_client()

        assert hasattr(client, "connect")
        assert hasattr(client, "disconnect")
        assert hasattr(client, "send")
        assert hasattr(client, "receive")
        assert hasattr(client, "close")
        assert hasattr(client, "is_connected")
        assert hasattr(client, "is_available")

    def test_client_is_available_property(self):
        """Test client availability property."""
        from server.messaging.zmq_client import create_zmq_client, is_zmq_available

        client = create_zmq_client()

        # If ZMQ is available, client should report available
        # If not, NoOpClient should report not available
        if is_zmq_available():
            assert client.is_available is True
        else:
            assert client.is_available is False

    def test_noop_client_operations_safe(self):
        """Test NoOp client operations don't crash."""
        from server.messaging.zmq_client import NoOpClient

        client = NoOpClient()

        # These should all be safe no-ops
        assert client.connect("tcp://localhost:5555") is False
        assert client.disconnect() is True
        assert client.send(b"test") is False
        assert client.receive() is None
        assert client.is_connected is False
        assert client.is_available is False

        # Close should not raise
        client.close()


class TestAPIHealthEndpoint:
    """Test API health endpoint with platform info."""

    def test_health_endpoint(self):
        """Test health endpoint returns platform info."""
        pytest.importorskip("httpx")
        from server.api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "services" in data
        assert "platform" in data
        assert "features" in data

    def test_status_endpoint(self):
        """Test status endpoint returns feature info."""
        pytest.importorskip("httpx")
        from server.api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/v1/status")

        assert response.status_code == 200

        data = response.json()
        assert "api_version" in data
        assert "core_services" in data
        assert "available_endpoints" in data


class TestErrorHandling:
    """Test robust error handling."""

    def test_invalid_hex_in_authenticate(self):
        """Test authentication handles invalid hex gracefully."""
        pytest.importorskip("httpx")
        from server.api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.post(
            "/api/v1/authenticate",
            json={
                "challenge_id": "test-id",
                "challenge_response": "not-valid-hex-XYZ!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error_message" in data

    def test_unknown_key_challenge(self):
        """Test challenge request for unknown key."""
        pytest.importorskip("httpx")
        from server.api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.post(
            "/api/v1/challenge",
            json={"key_id": "nonexistent-key-id"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error_message" in data
