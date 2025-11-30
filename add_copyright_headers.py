#!/usr/bin/env python3
# ==============================================================================
# DNALockOS - DNA-Key Authentication System
# Copyright (c) 2025 WeNova Interactive
# Legal Owner: Kayden Shawn Massengill (Operating as WeNova Interactive)
# ALL RIGHTS RESERVED.
# ==============================================================================
#
# PROPRIETARY AND CONFIDENTIAL - COMMERCIAL SOFTWARE
#
# This software is the exclusive property of WeNova Interactive, legally owned
# and operated by Kayden Shawn Massengill. This is NOT free software. This is
# NOT open source. This is COMMERCIAL SOFTWARE intended for LICENSED SALE ONLY.
#
# UNAUTHORIZED ACCESS, USE, COPYING, MODIFICATION, MERGER, PUBLICATION,
# DISTRIBUTION, SUBLICENSING, AND/OR SALE IS STRICTLY PROHIBITED.
#
# Violators will be prosecuted to the fullest extent of applicable law.
#
# License: Proprietary Commercial License Required
# Contact: WeNova Interactive
# ==============================================================================
"""
DNALockOS Proprietary Copyright Header Management System

Production-grade utility for injecting and managing proprietary copyright
headers across the entire DNALockOS codebase. This tool ensures all source
files properly declare:

1. Ownership by WeNova Interactive (Kayden Shawn Massengill)
2. Commercial/proprietary nature of the software
3. Prohibition of unauthorized use
4. Legal protections and enforcement rights

USAGE:
    python add_copyright_headers.py --force    # Update all files
    python add_copyright_headers.py --dry-run  # Preview changes
    python add_copyright_headers.py --verbose  # Show all processing

This script is part of the DNALockOS production release preparation process.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ==============================================================================
# PROPRIETARY HEADER DEFINITIONS
# ==============================================================================

# The definitive copyright notice for all files
COPYRIGHT_YEAR = "2025"
COMPANY_NAME = "WeNova Interactive"
LEGAL_OWNER = "Kayden Shawn Massengill"
OWNERSHIP_STATEMENT = f"{LEGAL_OWNER} (Operating as {COMPANY_NAME})"

# ==============================================================================
# PYTHON HEADER - For .py files
# ==============================================================================
PYTHON_HEADER = f'''"""
==============================================================================
DNALockOS - DNA-Key Authentication System
Copyright (c) {COPYRIGHT_YEAR} {COMPANY_NAME}
==============================================================================

OWNERSHIP AND LEGAL NOTICE:

This software and all associated intellectual property is the exclusive
property of {COMPANY_NAME}, legally owned and operated by:

    {LEGAL_OWNER}

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

For licensing inquiries: {COMPANY_NAME}
==============================================================================
"""

'''

# ==============================================================================
# JAVASCRIPT/JSX/TYPESCRIPT HEADER - For .js, .jsx, .ts, .tsx files
# ==============================================================================
JAVASCRIPT_HEADER = f'''/**
 * =============================================================================
 * DNALockOS - DNA-Key Authentication System
 * Copyright (c) {COPYRIGHT_YEAR} {COMPANY_NAME}
 * =============================================================================
 *
 * OWNERSHIP AND LEGAL NOTICE:
 *
 * This software and all associated intellectual property is the exclusive
 * property of {COMPANY_NAME}, legally owned and operated by:
 *
 *     {LEGAL_OWNER}
 *
 * COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE
 *
 * This is proprietary commercial software. It is NOT free software. It is NOT
 * open source software. This software is developed for commercial sale and
 * requires a valid commercial license for ANY use.
 *
 * STRICT PROHIBITION NOTICE:
 *
 * Without a valid commercial license agreement, you are PROHIBITED from:
 *   - Using this software for any purpose
 *   - Copying, reproducing, or duplicating this software
 *   - Modifying, adapting, or creating derivative works
 *   - Distributing, publishing, or transferring this software
 *   - Reverse engineering, decompiling, or disassembling this software
 *   - Sublicensing or permitting any third-party access
 *
 * LEGAL ENFORCEMENT:
 *
 * Unauthorized use will be prosecuted to the maximum extent of applicable law.
 *
 * For licensing inquiries: {COMPANY_NAME}
 * =============================================================================
 */

'''

# ==============================================================================
# HTML HEADER - For .html, .htm files
# ==============================================================================
HTML_HEADER = f'''<!--
===============================================================================
DNALockOS - DNA-Key Authentication System
Copyright (c) {COPYRIGHT_YEAR} {COMPANY_NAME}
===============================================================================

OWNERSHIP AND LEGAL NOTICE:

This software and all associated intellectual property is the exclusive
property of {COMPANY_NAME}, legally owned and operated by:

    {LEGAL_OWNER}

COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE

This is proprietary commercial software developed for commercial sale only.
A valid commercial license is required for ANY use.

STRICT PROHIBITION: Unauthorized use, copying, modification, or distribution
is strictly prohibited and will be prosecuted to the fullest extent of law.

For licensing inquiries: {COMPANY_NAME}
===============================================================================
-->

'''

# ==============================================================================
# CSS/SCSS HEADER - For .css, .scss files
# ==============================================================================
CSS_HEADER = f'''/*
 * =============================================================================
 * DNALockOS - DNA-Key Authentication System
 * Copyright (c) {COPYRIGHT_YEAR} {COMPANY_NAME}
 * =============================================================================
 *
 * OWNERSHIP: {LEGAL_OWNER} (Operating as {COMPANY_NAME})
 *
 * COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE
 *
 * This is proprietary commercial software. A valid commercial license is
 * required for ANY use. Unauthorized use, copying, modification, or
 * distribution is strictly prohibited and will be prosecuted.
 *
 * For licensing inquiries: {COMPANY_NAME}
 * =============================================================================
 */

'''

# ==============================================================================
# YAML HEADER - For .yaml, .yml files
# ==============================================================================
YAML_HEADER = f'''# ==============================================================================
# DNALockOS - DNA-Key Authentication System
# Copyright (c) {COPYRIGHT_YEAR} {COMPANY_NAME}
# ==============================================================================
#
# OWNERSHIP: {LEGAL_OWNER} (Operating as {COMPANY_NAME})
#
# COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE
#
# This is proprietary commercial software. A valid commercial license is
# required for ANY use. Unauthorized use, copying, modification, or
# distribution is strictly prohibited and will be prosecuted.
#
# For licensing inquiries: {COMPANY_NAME}
# ==============================================================================

'''

# ==============================================================================
# SHELL HEADER - For .sh, .bash files
# ==============================================================================
SHELL_HEADER = f'''#!/bin/bash
# ==============================================================================
# DNALockOS - DNA-Key Authentication System
# Copyright (c) {COPYRIGHT_YEAR} {COMPANY_NAME}
# ==============================================================================
#
# OWNERSHIP: {LEGAL_OWNER} (Operating as {COMPANY_NAME})
#
# COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE
#
# This is proprietary commercial software. A valid commercial license is
# required for ANY use. Unauthorized use, copying, modification, or
# distribution is strictly prohibited and will be prosecuted.
#
# For licensing inquiries: {COMPANY_NAME}
# ==============================================================================

'''

# ==============================================================================
# MARKDOWN HEADER - For .md files
# ==============================================================================
MARKDOWN_HEADER = f'''<!--
DNALockOS - DNA-Key Authentication System
Copyright (c) {COPYRIGHT_YEAR} {COMPANY_NAME}
Legal Owner: {LEGAL_OWNER} (Operating as {COMPANY_NAME})

PROPRIETARY AND CONFIDENTIAL - COMMERCIAL SOFTWARE
This is NOT free software. This is NOT open source. Commercial license required.
Unauthorized use is strictly prohibited.
-->

'''


class FileType(Enum):
    """Supported file types for header injection."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JSX = "jsx"
    TYPESCRIPT = "typescript"
    TSX = "tsx"
    HTML = "html"
    CSS = "css"
    SCSS = "scss"
    YAML = "yaml"
    SHELL = "shell"
    MARKDOWN = "markdown"


# Header mapping by file type
HEADERS: Dict[FileType, str] = {
    FileType.PYTHON: PYTHON_HEADER,
    FileType.JAVASCRIPT: JAVASCRIPT_HEADER,
    FileType.JSX: JAVASCRIPT_HEADER,
    FileType.TYPESCRIPT: JAVASCRIPT_HEADER,
    FileType.TSX: JAVASCRIPT_HEADER,
    FileType.HTML: HTML_HEADER,
    FileType.CSS: CSS_HEADER,
    FileType.SCSS: CSS_HEADER,
    FileType.YAML: YAML_HEADER,
    FileType.SHELL: SHELL_HEADER,
    FileType.MARKDOWN: MARKDOWN_HEADER,
}

# Extension to file type mapping
EXTENSION_MAP: Dict[str, FileType] = {
    ".py": FileType.PYTHON,
    ".pyw": FileType.PYTHON,
    ".js": FileType.JAVASCRIPT,
    ".mjs": FileType.JAVASCRIPT,
    ".cjs": FileType.JAVASCRIPT,
    ".jsx": FileType.JSX,
    ".ts": FileType.TYPESCRIPT,
    ".tsx": FileType.TSX,
    ".html": FileType.HTML,
    ".htm": FileType.HTML,
    ".css": FileType.CSS,
    ".scss": FileType.SCSS,
    ".sass": FileType.SCSS,
    ".less": FileType.CSS,
    ".yaml": FileType.YAML,
    ".yml": FileType.YAML,
    ".sh": FileType.SHELL,
    ".bash": FileType.SHELL,
    ".zsh": FileType.SHELL,
    ".md": FileType.MARKDOWN,
    ".markdown": FileType.MARKDOWN,
}

# Directories to always skip
SKIP_DIRECTORIES: Set[str] = {
    ".git",
    ".svn",
    ".hg",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "virtualenv",
    "dist",
    "build",
    "target",
    ".pytest_cache",
    ".hypothesis",
    ".mypy_cache",
    ".tox",
    ".nox",
    "htmlcov",
    "coverage",
    ".coverage",
    "site",
    ".next",
    "out",
    ".cache",
    ".parcel-cache",
    ".nuxt",
    ".output",
    "eggs",
    ".eggs",
    "*.egg-info",
    "lib",
    "lib64",
    "parts",
    "sdist",
    "wheels",
    ".installed.cfg",
}

# Files to always skip
SKIP_FILES: Set[str] = {
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "tsconfig.json",
    "jsconfig.json",
    ".eslintrc",
    ".eslintrc.js",
    ".eslintrc.json",
    ".prettierrc",
    ".prettierrc.js",
    ".prettierrc.json",
    "babel.config.js",
    "babel.config.json",
    ".babelrc",
    "jest.config.js",
    "jest.config.ts",
    "webpack.config.js",
    "rollup.config.js",
    "vite.config.js",
    "vite.config.ts",
    "next.config.js",
    "next.config.mjs",
    "tailwind.config.js",
    "postcss.config.js",
    ".gitignore",
    ".dockerignore",
    ".npmignore",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Makefile",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-mobile.txt",
    "setup.cfg",
    "pyproject.toml",
    "poetry.lock",
    "Pipfile",
    "Pipfile.lock",
    "conftest.py",
    "pytest.ini",
    "tox.ini",
    ".coveragerc",
    "mypy.ini",
    ".flake8",
    "LICENSE",
    "COPYRIGHT",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
}

# Patterns indicating existing copyright (case-insensitive)
COPYRIGHT_INDICATORS: List[str] = [
    r"copyright\s*\(c\)",
    r"copyright\s*©",
    r"copyright\s+\d{4}",
    r"all\s+rights\s+reserved",
    r"proprietary\s+and\s+confidential",
    r"wennova\s+interactive",
    r"kayden\s+shawn\s+massengill",
    r"commercial\s+software",
    r"not\s+free\s+software",
    r"not\s+open\s+source",
    r"dnalockos",
    r"licensed?\s+sale",
]


@dataclass
class ProcessingResult:
    """Result of processing a single file."""
    filepath: Path
    status: str  # 'updated', 'skipped', 'error'
    reason: str
    file_type: Optional[FileType] = None


@dataclass
class ProcessingSummary:
    """Summary of all processing."""
    total_scanned: int = 0
    total_updated: int = 0
    total_skipped: int = 0
    total_errors: int = 0
    results: List[ProcessingResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None


def has_copyright_header(content: str) -> bool:
    """Check if content already has a copyright header."""
    # Check first 3000 characters for any copyright indicator
    header_section = content[:3000].lower()
    
    for pattern in COPYRIGHT_INDICATORS:
        if re.search(pattern, header_section, re.IGNORECASE):
            return True
    
    return False


def extract_shebang(content: str) -> Tuple[str, str]:
    """Extract shebang line from content if present."""
    lines = content.split('\n', 1)
    if lines and lines[0].startswith('#!'):
        shebang = lines[0] + '\n'
        rest = lines[1] if len(lines) > 1 else ''
        return shebang, rest
    return '', content


def remove_existing_header(content: str, file_type: FileType) -> str:
    """Remove existing copyright/proprietary headers from content."""
    
    if file_type == FileType.PYTHON:
        # Remove leading docstrings that contain copyright
        pattern = r'^\\s*"""[\\s\\S]*?"""\\s*\\n?'
        match = re.match(pattern, content)
        while match:
            matched_text = match.group(0)
            if has_copyright_header(matched_text):
                content = content[len(matched_text):].lstrip()
                match = re.match(pattern, content)
            else:
                break
    
    elif file_type in (FileType.JAVASCRIPT, FileType.JSX, FileType.TYPESCRIPT, 
                       FileType.TSX, FileType.CSS, FileType.SCSS):
        # Remove leading block comments that contain copyright
        pattern = r'^\\s*/\\*[\\s\\S]*?\\*/\\s*\\n?'
        match = re.match(pattern, content)
        while match:
            matched_text = match.group(0)
            if has_copyright_header(matched_text):
                content = content[len(matched_text):].lstrip()
                match = re.match(pattern, content)
            else:
                break
    
    elif file_type == FileType.HTML:
        # Remove leading HTML comments that contain copyright
        pattern = r'^\\s*<!--[\\s\\S]*?-->\\s*\\n?'
        match = re.match(pattern, content)
        while match:
            matched_text = match.group(0)
            if has_copyright_header(matched_text):
                content = content[len(matched_text):].lstrip()
                match = re.match(pattern, content)
            else:
                break
    
    elif file_type in (FileType.YAML, FileType.SHELL):
        # Remove leading comment blocks that contain copyright
        lines = content.split('\\n')
        new_lines = []
        in_header = True
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if in_header:
                # Skip shebang (handled separately)
                if i == 0 and stripped.startswith('#!'):
                    continue
                # Skip comment lines that are part of copyright header
                if stripped.startswith('#'):
                    if has_copyright_header(line):
                        continue
                    # Check if it's a separator line
                    if stripped == '#' or re.match(r'^#\\s*=+\\s*$', stripped):
                        continue
                # Skip empty lines in header
                if stripped == '':
                    continue
                # Real content starts here
                in_header = False
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        content = '\\n'.join(new_lines)
    
    elif file_type == FileType.MARKDOWN:
        # Remove leading HTML comments in markdown
        pattern = r'^\\s*<!--[\\s\\S]*?-->\\s*\\n?'
        match = re.match(pattern, content)
        while match:
            matched_text = match.group(0)
            if has_copyright_header(matched_text):
                content = content[len(matched_text):].lstrip()
                match = re.match(pattern, content)
            else:
                break
    
    return content


def process_file(
    filepath: Path,
    force: bool = False,
    dry_run: bool = False
) -> ProcessingResult:
    """Process a single file to add/update copyright header."""
    
    # Determine file type
    ext = filepath.suffix.lower()
    file_type = EXTENSION_MAP.get(ext)
    
    if file_type is None:
        return ProcessingResult(filepath, 'skipped', 'Unknown file type', None)
    
    if filepath.name in SKIP_FILES:
        return ProcessingResult(filepath, 'skipped', 'In skip list', file_type)
    
    # Read file content
    try:
        content = filepath.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            content = filepath.read_text(encoding='latin-1')
        except Exception as e:
            return ProcessingResult(filepath, 'error', f'Read error: {e}', file_type)
    except Exception as e:
        return ProcessingResult(filepath, 'error', f'Read error: {e}', file_type)
    
    # Skip empty files
    if not content.strip():
        return ProcessingResult(filepath, 'skipped', 'Empty file', file_type)
    
    # Check for existing header
    has_header = has_copyright_header(content)
    
    if has_header and not force:
        return ProcessingResult(filepath, 'skipped', 'Already has header (use --force)', file_type)
    
    # Get the appropriate header template
    header = HEADERS.get(file_type, '')
    if not header:
        return ProcessingResult(filepath, 'skipped', 'No header template', file_type)
    
    # Handle shebang for shell scripts and Python
    shebang = ''
    if file_type in (FileType.PYTHON, FileType.SHELL):
        shebang, content = extract_shebang(content)
    
    # Remove existing header if present
    if has_header:
        content = remove_existing_header(content, file_type)
    
    # Build new content
    if file_type == FileType.SHELL:
        # Shell header already includes shebang
        if shebang:
            # Replace default shebang with actual one
            new_content = header.replace('#!/bin/bash\\n', shebang) + content
        else:
            new_content = header + content
    elif shebang:
        new_content = shebang + header + content
    else:
        new_content = header + content
    
    # Write if not dry run
    if not dry_run:
        try:
            filepath.write_text(new_content, encoding='utf-8')
        except Exception as e:
            return ProcessingResult(filepath, 'error', f'Write error: {e}', file_type)
    
    status = 'would update' if dry_run else 'updated'
    reason = 'Header replaced' if has_header else 'Header added'
    return ProcessingResult(filepath, status, reason, file_type)


def process_directory(
    root_dir: Path,
    force: bool = False,
    dry_run: bool = False,
    verbose: bool = False
) -> ProcessingSummary:
    """Process all files in a directory recursively."""
    
    summary = ProcessingSummary()
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRECTORIES]
        
        for filename in filenames:
            filepath = Path(dirpath) / filename
            
            # Skip files without recognized extensions
            if filepath.suffix.lower() not in EXTENSION_MAP:
                continue
            
            summary.total_scanned += 1
            
            result = process_file(filepath, force, dry_run)
            summary.results.append(result)
            
            if result.status in ('updated', 'would update'):
                summary.total_updated += 1
                print(f"  ✓ {result.status.upper()}: {result.filepath}")
            elif result.status == 'error':
                summary.total_errors += 1
                print(f"  ✗ ERROR: {result.filepath} - {result.reason}")
            else:
                summary.total_skipped += 1
                if verbose:
                    print(f"  - SKIPPED: {result.filepath} ({result.reason})")
    
    summary.end_time = datetime.now(timezone.utc)
    return summary


def print_banner():
    """Print the script banner."""
    print()
    print("=" * 78)
    print("  DNALockOS PROPRIETARY COPYRIGHT HEADER MANAGEMENT SYSTEM")
    print("=" * 78)
    print()
    print("  SOFTWARE OWNER:    WeNova Interactive")
    print("  LEGAL OWNER:       Kayden Shawn Massengill")
    print("  OWNERSHIP STATUS:  Operating as WeNova Interactive")
    print()
    print("  SOFTWARE TYPE:     PROPRIETARY COMMERCIAL SOFTWARE")
    print("  LICENSE TYPE:      COMMERCIAL LICENSE REQUIRED")
    print("  FREE/OPEN SOURCE:  NO - This is NOT free or open source software")
    print()
    print("=" * 78)


def print_summary(summary: ProcessingSummary, dry_run: bool):
    """Print processing summary."""
    duration = (summary.end_time - summary.start_time).total_seconds()
    
    print()
    print("=" * 78)
    print("  PROCESSING SUMMARY")
    print("=" * 78)
    print()
    print(f"  Files Scanned:   {summary.total_scanned}")
    print(f"  Files Updated:   {summary.total_updated}")
    print(f"  Files Skipped:   {summary.total_skipped}")
    print(f"  Errors:          {summary.total_errors}")
    print(f"  Duration:        {duration:.2f} seconds")
    print()
    
    if dry_run:
        print("  MODE: DRY RUN - No files were actually modified")
        print()
        print("  To apply changes, run without --dry-run flag")
        print("  To replace existing headers, add --force flag")
    
    print()
    print("=" * 78)
    print(f"  All files are now marked as property of:")
    print(f"  {COMPANY_NAME} ({LEGAL_OWNER})")
    print("=" * 78)
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Add proprietary copyright headers to all DNALockOS source files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_copyright_headers.py                    # Preview changes (dry run)
  python add_copyright_headers.py --force            # Update all files
  python add_copyright_headers.py --force --verbose  # Update with details

This script ensures all source files properly declare ownership by:
  WeNova Interactive (Kayden Shawn Massengill)
"""
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Preview changes without modifying files (default)'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Actually modify files and replace existing headers'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show all files including skipped ones'
    )
    
    parser.add_argument(
        '--directory', '-d',
        type=str,
        default='.',
        help='Root directory to process (default: current)'
    )
    
    args = parser.parse_args()
    
    # If --force is specified, disable dry_run
    dry_run = not args.force
    
    root_dir = Path(args.directory).resolve()
    
    if not root_dir.exists():
        print(f"Error: Directory not found: {root_dir}")
        sys.exit(1)
    
    print_banner()
    
    print(f"  Processing: {root_dir}")
    print()
    
    if dry_run:
        print("  MODE: DRY RUN (use --force to apply changes)")
    else:
        print("  MODE: APPLYING CHANGES")
    
    print()
    print("-" * 78)
    
    summary = process_directory(root_dir, args.force, dry_run, args.verbose)
    
    print("-" * 78)
    
    print_summary(summary, dry_run)
    
    # Exit with error code if there were errors
    if summary.total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
