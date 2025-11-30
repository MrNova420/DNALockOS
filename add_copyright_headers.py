#!/usr/bin/env python3
"""
DNALockOS - Copyright Header Injection Script

This script adds copyright headers to all source files in the project.
Copyright (c) 2025 WeNova Interactive - Kayden Shawn Massengill

Usage:
    python add_copyright_headers.py [--dry-run] [--verbose]
"""

import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional

# Copyright header templates for different file types
COPYRIGHT_HEADERS: Dict[str, str] = {
    "python": '''"""
DNALockOS - DNA-Key Authentication System
Copyright (c) 2025 WeNova Interactive
Legal Owner: Kayden Shawn Massengill
ALL RIGHTS RESERVED.

PROPRIETARY AND CONFIDENTIAL
This is commercial software. Unauthorized copying, modification,
distribution, or use is strictly prohibited.
"""

''',
    "javascript": '''/**
 * DNALockOS - DNA-Key Authentication System
 * Copyright (c) 2025 WeNova Interactive
 * Legal Owner: Kayden Shawn Massengill
 * ALL RIGHTS RESERVED.
 *
 * PROPRIETARY AND CONFIDENTIAL
 * This is commercial software. Unauthorized copying, modification,
 * distribution, or use is strictly prohibited.
 */

''',
    "jsx": '''/**
 * DNALockOS - DNA-Key Authentication System
 * Copyright (c) 2025 WeNova Interactive
 * Legal Owner: Kayden Shawn Massengill
 * ALL RIGHTS RESERVED.
 *
 * PROPRIETARY AND CONFIDENTIAL
 * This is commercial software. Unauthorized copying, modification,
 * distribution, or use is strictly prohibited.
 */

''',
    "html": '''<!--
  DNALockOS - DNA-Key Authentication System
  Copyright (c) 2025 WeNova Interactive
  Legal Owner: Kayden Shawn Massengill
  ALL RIGHTS RESERVED.

  PROPRIETARY AND CONFIDENTIAL
  This is commercial software. Unauthorized copying, modification,
  distribution, or use is strictly prohibited.
-->

''',
    "css": '''/*
 * DNALockOS - DNA-Key Authentication System
 * Copyright (c) 2025 WeNova Interactive
 * Legal Owner: Kayden Shawn Massengill
 * ALL RIGHTS RESERVED.
 *
 * PROPRIETARY AND CONFIDENTIAL
 * This is commercial software. Unauthorized copying, modification,
 * distribution, or use is strictly prohibited.
 */

''',
    "yaml": '''# DNALockOS - DNA-Key Authentication System
# Copyright (c) 2025 WeNova Interactive
# Legal Owner: Kayden Shawn Massengill
# ALL RIGHTS RESERVED.
#
# PROPRIETARY AND CONFIDENTIAL
# This is commercial software. Unauthorized copying, modification,
# distribution, or use is strictly prohibited.

''',
    "shell": '''#!/bin/bash
# DNALockOS - DNA-Key Authentication System
# Copyright (c) 2025 WeNova Interactive
# Legal Owner: Kayden Shawn Massengill
# ALL RIGHTS RESERVED.
#
# PROPRIETARY AND CONFIDENTIAL
# This is commercial software. Unauthorized copying, modification,
# distribution, or use is strictly prohibited.

''',
}

# File extension to type mapping
EXTENSION_MAP: Dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "jsx",
    ".ts": "javascript",
    ".tsx": "jsx",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "css",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".sh": "shell",
    ".bash": "shell",
}

# Directories to skip
SKIP_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    ".pytest_cache",
    ".hypothesis",
    ".mypy_cache",
    "htmlcov",
    "site",
    ".tox",
}

# Files to skip
SKIP_FILES = {
    "__init__.py",  # Skip empty init files
    "setup.py",
    "conftest.py",
}


def has_copyright_header(content: str, file_type: str) -> bool:
    """Check if file already has a copyright header."""
    copyright_indicators = [
        "Copyright (c)",
        "Copyright ©",
        "WeNova Interactive",
        "Kayden Shawn Massengill",
        "DNALockOS",
        "All Rights Reserved",
    ]
    
    # Check first 1000 characters for copyright
    header_section = content[:1000].lower()
    
    for indicator in copyright_indicators:
        if indicator.lower() in header_section:
            return True
    
    return False


def add_copyright_header(filepath: Path, dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Add copyright header to a file if not present.
    
    Returns True if header was added (or would be added in dry-run mode).
    """
    ext = filepath.suffix.lower()
    file_type = EXTENSION_MAP.get(ext)
    
    if file_type is None:
        if verbose:
            print(f"  Skipping (unknown type): {filepath}")
        return False
    
    if filepath.name in SKIP_FILES:
        if verbose:
            print(f"  Skipping (skip file): {filepath}")
        return False
    
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, IOError) as e:
        print(f"  Error reading {filepath}: {e}")
        return False
    
    # Skip empty files
    if not content.strip():
        if verbose:
            print(f"  Skipping (empty): {filepath}")
        return False
    
    # Skip if already has copyright
    if has_copyright_header(content, file_type):
        if verbose:
            print(f"  Skipping (has copyright): {filepath}")
        return False
    
    # Get appropriate header
    header = COPYRIGHT_HEADERS.get(file_type, "")
    if not header:
        if verbose:
            print(f"  Skipping (no header template): {filepath}")
        return False
    
    # Handle shebang lines for Python/Shell
    new_content = content
    if file_type in ("python", "shell"):
        lines = content.split("\n")
        if lines and lines[0].startswith("#!"):
            # Preserve shebang, add header after
            shebang = lines[0] + "\n"
            rest = "\n".join(lines[1:])
            # Adjust header for Python (remove the empty docstring start if shebang present)
            if file_type == "python":
                new_content = shebang + header + rest
            else:
                # For shell, header already has shebang
                new_content = header.replace("#!/bin/bash\n", shebang) + rest
        else:
            new_content = header + content
    else:
        new_content = header + content
    
    if dry_run:
        print(f"  Would add header to: {filepath}")
        return True
    
    try:
        filepath.write_text(new_content, encoding="utf-8")
        print(f"  Added header to: {filepath}")
        return True
    except IOError as e:
        print(f"  Error writing {filepath}: {e}")
        return False


def process_directory(
    root_dir: Path,
    dry_run: bool = False,
    verbose: bool = False
) -> tuple:
    """
    Process all files in directory recursively.
    
    Returns (files_processed, files_modified).
    """
    files_processed = 0
    files_modified = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        
        for filename in filenames:
            filepath = Path(dirpath) / filename
            
            # Skip files without recognized extensions
            if filepath.suffix.lower() not in EXTENSION_MAP:
                continue
            
            files_processed += 1
            
            if add_copyright_header(filepath, dry_run, verbose):
                files_modified += 1
    
    return files_processed, files_modified


def main():
    parser = argparse.ArgumentParser(
        description="Add copyright headers to DNALockOS source files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all files being processed"
    )
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        default=".",
        help="Directory to process (default: current directory)"
    )
    
    args = parser.parse_args()
    
    root_dir = Path(args.directory).resolve()
    
    print("=" * 70)
    print("DNALockOS Copyright Header Injection")
    print("Copyright (c) 2025 WeNova Interactive - Kayden Shawn Massengill")
    print("=" * 70)
    print(f"\nProcessing directory: {root_dir}")
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")
    else:
        print()
    
    files_processed, files_modified = process_directory(
        root_dir,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    print("\n" + "=" * 70)
    print(f"Files scanned: {files_processed}")
    print(f"Files {'would be modified' if args.dry_run else 'modified'}: {files_modified}")
    print("=" * 70)
    
    if args.dry_run and files_modified > 0:
        print("\nRun without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
