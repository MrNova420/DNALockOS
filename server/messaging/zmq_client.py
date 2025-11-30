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
DNA-Key Authentication System - ZMQ Client with Fallback

Provides ZeroMQ-based messaging client with graceful fallback when
pyzmq is not available (e.g., on Termux/Android or constrained environments).

Features:
- Optional pyzmq dependency
- NoOp fallback client for graceful degradation
- Clear logging when ZMQ is unavailable
- Thread-safe client management
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List
import warnings


# Track ZMQ availability
_ZMQ_AVAILABLE: Optional[bool] = None


def is_zmq_available() -> bool:
    """
    Check if pyzmq is available.

    Returns:
        True if pyzmq is installed and importable.
    """
    global _ZMQ_AVAILABLE
    if _ZMQ_AVAILABLE is None:
        try:
            import zmq  # noqa: F401
            _ZMQ_AVAILABLE = True
        except ImportError:
            _ZMQ_AVAILABLE = False
    return _ZMQ_AVAILABLE


class BaseZMQClient(ABC):
    """Abstract base class for ZMQ clients."""

    @abstractmethod
    def connect(self, endpoint: str) -> bool:
        """Connect to a ZMQ endpoint."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the current endpoint."""
        pass

    @abstractmethod
    def send(self, message: bytes, flags: int = 0) -> bool:
        """Send a message."""
        pass

    @abstractmethod
    def receive(self, flags: int = 0) -> Optional[bytes]:
        """Receive a message."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the client and release resources."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if client is connected."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if ZMQ is available."""
        pass


class ZMQClient(BaseZMQClient):
    """
    ZeroMQ client for inter-service messaging.

    Provides pub/sub, request/reply, and push/pull messaging patterns
    for distributed DNALockOS deployments.
    """

    def __init__(
        self,
        socket_type: Optional[int] = None,
        context: Optional[Any] = None,
    ):
        """
        Initialize ZMQ client.

        Args:
            socket_type: ZMQ socket type (e.g., zmq.REQ, zmq.SUB).
                        Defaults to zmq.REQ if not specified.
            context: Optional ZMQ context. Creates new one if not provided.

        Raises:
            ImportError: If pyzmq is not installed.
        """
        try:
            import zmq
        except ImportError as e:
            raise ImportError(
                "pyzmq is not installed. Install it with: pip install pyzmq"
            ) from e

        self._zmq = zmq
        self._context = context or zmq.Context()
        self._socket_type = socket_type or zmq.REQ
        self._socket: Optional[Any] = None
        self._endpoint: Optional[str] = None
        self._connected = False

    def connect(self, endpoint: str) -> bool:
        """
        Connect to a ZMQ endpoint.

        Args:
            endpoint: ZMQ endpoint string (e.g., "tcp://localhost:5555").

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            if self._socket is not None:
                self._socket.close()

            self._socket = self._context.socket(self._socket_type)
            self._socket.connect(endpoint)
            self._endpoint = endpoint
            self._connected = True
            return True
        except Exception as e:
            _log_error(f"Failed to connect to {endpoint}: {e}")
            self._connected = False
            return False

    def disconnect(self) -> bool:
        """
        Disconnect from the current endpoint.

        Returns:
            True if disconnection successful, False otherwise.
        """
        try:
            if self._socket is not None:
                self._socket.disconnect(self._endpoint)
                self._connected = False
            return True
        except Exception as e:
            _log_error(f"Failed to disconnect: {e}")
            return False

    def send(self, message: bytes, flags: int = 0) -> bool:
        """
        Send a message.

        Args:
            message: Message bytes to send.
            flags: Optional ZMQ send flags.

        Returns:
            True if send successful, False otherwise.
        """
        if self._socket is None:
            _log_error("Cannot send: socket not initialized")
            return False

        try:
            self._socket.send(message, flags)
            return True
        except Exception as e:
            _log_error(f"Failed to send message: {e}")
            return False

    def receive(self, flags: int = 0) -> Optional[bytes]:
        """
        Receive a message.

        Args:
            flags: Optional ZMQ receive flags.

        Returns:
            Received message bytes, or None if receive failed.
        """
        if self._socket is None:
            _log_error("Cannot receive: socket not initialized")
            return None

        try:
            return self._socket.recv(flags)
        except Exception as e:
            _log_error(f"Failed to receive message: {e}")
            return None

    def close(self) -> None:
        """Close the client and release resources."""
        try:
            if self._socket is not None:
                self._socket.close()
                self._socket = None
            self._connected = False
        except Exception as e:
            _log_error(f"Error closing socket: {e}")

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    @property
    def is_available(self) -> bool:
        """Check if ZMQ is available."""
        return True


class NoOpClient(BaseZMQClient):
    """
    No-operation ZMQ client for environments without pyzmq.

    Provides a graceful fallback that logs warnings but doesn't crash
    the application. All operations are no-ops that return safe defaults.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initialize NoOp client.

        Logs a warning that ZMQ messaging is disabled.
        """
        self._warned = False

    def _warn_once(self) -> None:
        """Log warning once about ZMQ being unavailable."""
        if not self._warned:
            _log_warning(
                "pyzmq not installed; ZMQ messaging disabled on this platform. "
                "Install with: pip install pyzmq"
            )
            self._warned = True

    def connect(self, endpoint: str) -> bool:
        """No-op connect that logs warning."""
        self._warn_once()
        return False

    def disconnect(self) -> bool:
        """No-op disconnect."""
        return True

    def send(self, message: bytes, flags: int = 0) -> bool:
        """No-op send that logs warning."""
        self._warn_once()
        return False

    def receive(self, flags: int = 0) -> Optional[bytes]:
        """No-op receive that returns None."""
        self._warn_once()
        return None

    def close(self) -> None:
        """No-op close."""
        pass

    @property
    def is_connected(self) -> bool:
        """Always returns False for NoOp client."""
        return False

    @property
    def is_available(self) -> bool:
        """Always returns False for NoOp client."""
        return False


def create_zmq_client(
    socket_type: Optional[int] = None,
    context: Optional[Any] = None,
) -> BaseZMQClient:
    """
    Create the best available ZMQ client.

    Returns a real ZMQ client if pyzmq is available, otherwise returns
    a no-op client that gracefully handles all operations without crashing.

    Args:
        socket_type: ZMQ socket type (e.g., zmq.REQ, zmq.SUB).
        context: Optional ZMQ context.

    Returns:
        A ZMQ client instance (real or no-op).

    Example:
        >>> client = create_zmq_client()
        >>> if client.is_available:
        ...     client.connect("tcp://localhost:5555")
        ...     client.send(b"Hello")
    """
    if is_zmq_available():
        try:
            return ZMQClient(socket_type, context)
        except Exception as e:
            _log_error(f"Failed to create ZMQ client: {e}")
            return NoOpClient()
    else:
        return NoOpClient()


def _log_warning(message: str) -> None:
    """Log warning message."""
    try:
        import structlog
        logger = structlog.get_logger()
        logger.warning(message, component="zmq_client")
    except ImportError:
        warnings.warn(message, UserWarning, stacklevel=3)


def _log_error(message: str) -> None:
    """Log error message."""
    try:
        import structlog
        logger = structlog.get_logger()
        logger.error(message, component="zmq_client")
    except ImportError:
        print(f"[ERROR] {message}")
