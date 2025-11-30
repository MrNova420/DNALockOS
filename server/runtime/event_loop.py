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
DNA-Key Authentication System - Event Loop Setup

Provides platform-aware event loop installation with graceful fallbacks.
On supported platforms (Linux, macOS), attempts to use uvloop for better
performance. Falls back to default asyncio on unsupported platforms
(Windows, Android/Termux) or when uvloop is not installed.
"""

import os
import sys
from typing import Dict, Any, Optional


# Platform detection constants
UNSUPPORTED_PLATFORMS = {"win32", "cygwin"}
ANDROID_INDICATORS = ["android", "termux"]


def is_android() -> bool:
    """
    Detect if running on Android/Termux environment.

    Returns:
        True if running on Android/Termux, False otherwise.
    """
    # Check platform string
    if any(indicator in sys.platform.lower() for indicator in ANDROID_INDICATORS):
        return True

    # Check environment variables commonly set in Termux
    termux_indicators = [
        "TERMUX_VERSION",
        "TERMUX_APP_PACKAGE_MANAGER",
        "PREFIX",  # Usually /data/data/com.termux/files/usr on Termux
    ]

    for indicator in termux_indicators:
        value = os.environ.get(indicator, "")
        if indicator == "PREFIX" and "termux" in value.lower():
            return True
        elif indicator != "PREFIX" and value:
            return True

    # Check for Android-specific paths
    android_paths = [
        "/data/data/com.termux",
        "/system/build.prop",
    ]

    for path in android_paths:
        if os.path.exists(path):
            return True

    return False


def is_unsupported_platform() -> bool:
    """
    Check if the current platform doesn't support uvloop.

    Returns:
        True if platform is unsupported for uvloop, False otherwise.
    """
    return sys.platform in UNSUPPORTED_PLATFORMS or is_android()


def get_platform_info() -> Dict[str, Any]:
    """
    Get detailed platform information for diagnostics.

    Returns:
        Dictionary containing platform details.
    """
    return {
        "platform": sys.platform,
        "python_version": sys.version,
        "python_version_info": {
            "major": sys.version_info.major,
            "minor": sys.version_info.minor,
            "micro": sys.version_info.micro,
        },
        "is_android": is_android(),
        "is_windows": sys.platform in {"win32", "cygwin"},
        "uvloop_supported": not is_unsupported_platform(),
        "uvloop_available": _check_uvloop_available(),
    }


def _check_uvloop_available() -> bool:
    """
    Check if uvloop is installed and importable.

    Returns:
        True if uvloop is available, False otherwise.
    """
    try:
        import uvloop  # noqa: F401
        return True
    except ImportError:
        return False


def install_best_event_loop() -> Optional[str]:
    """
    Install the fastest available async event loop for the current platform.

    On supported platforms (Linux, macOS), attempts to use uvloop for better
    async performance. Falls back to default asyncio on:
    - Windows
    - Android/Termux
    - Any platform where uvloop is not installed

    Returns:
        String indicating which event loop was installed:
        - "uvloop" if uvloop was successfully installed
        - "asyncio" if falling back to default asyncio
        - None if event loop setup failed

    Example:
        >>> from server.runtime.event_loop import install_best_event_loop
        >>> loop_type = install_best_event_loop()
        >>> print(f"Using {loop_type} event loop")
    """
    # Check for unsupported platforms first
    if is_unsupported_platform():
        platform_name = "Android/Termux" if is_android() else sys.platform
        _log_fallback(f"Platform {platform_name} does not support uvloop")
        return "asyncio"

    # Try to install uvloop
    try:
        import uvloop
        import warnings

        # Suppress deprecation warning for Python 3.12+
        # uvloop.install() still works, just deprecated in favor of uvloop.run()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            uvloop.install()

        _log_success("uvloop event loop installed successfully")
        return "uvloop"
    except ImportError:
        _log_fallback("uvloop not installed, using default asyncio")
        return "asyncio"
    except Exception as e:
        _log_fallback(f"Failed to install uvloop: {e}, using default asyncio")
        return "asyncio"


def _log_success(message: str) -> None:
    """Log success message if logging is available."""
    try:
        import structlog
        logger = structlog.get_logger()
        logger.info(message, component="event_loop")
    except ImportError:
        # Structlog not available, use print as fallback
        print(f"[INFO] {message}")


def _log_fallback(message: str) -> None:
    """Log fallback message if logging is available."""
    try:
        import structlog
        logger = structlog.get_logger()
        logger.warning(message, component="event_loop")
    except ImportError:
        # Structlog not available, use print as fallback
        print(f"[WARNING] {message}")
