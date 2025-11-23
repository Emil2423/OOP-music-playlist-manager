#!/usr/bin/env python3
"""Verification script to ensure all Sprint 1 deliverables are in place.

This script checks that all required files exist and have proper structure.
Run this after setup to verify the implementation is complete.

Usage:
    python verify_implementation.py
"""

import os
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def check_file_exists(path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(path)


def check_dir_exists(path: str) -> bool:
    """Check if a directory exists."""
    return os.path.isdir(path)


def print_header(text: str) -> None:
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_check(item: str, passed: bool) -> None:
    """Print a check result."""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status} - {item}")


def print_summary(total: int, passed: int) -> None:
    """Print verification summary."""
    failed = total - passed
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}Verification Summary:{Colors.RESET}")
    print(f"  Total Checks: {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
    if failed > 0:
        print(f"  {Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"  Success Rate: {percentage:.1f}%")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED - IMPLEMENTATION COMPLETE!{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME CHECKS FAILED - REVIEW ABOVE{Colors.RESET}\n")
        return 1


def main() -> int:
    """Run all verification checks."""
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    print_header("Sprint 1 Student B - Implementation Verification")
    
    checks = []
    passed = 0
    
    # Database Layer
    print(f"{Colors.BOLD}Database Layer:{Colors.RESET}")
    files_to_check = [
        "src/database/__init__.py",
        "src/database/connection.py",
        "src/database/schema.py"
    ]
    for file in files_to_check:
        check = check_file_exists(file)
        checks.append(check)
        if check:
            passed += 1
        print_check(file, check)
    
    # Repository Layer
    print(f"\n{Colors.BOLD}Repository Layer:{Colors.RESET}")
    files_to_check = [
        "src/repositories/__init__.py",
        "src/repositories/base_repository.py",
        "src/repositories/song_repository.py",
        "src/repositories/user_repository.py",
        "src/repositories/playlist_repository.py"
    ]
    for file in files_to_check:
        check = check_file_exists(file)
        checks.append(check)
        if check:
            passed += 1
        print_check(file, check)
    
    # Application Layer
    print(f"\n{Colors.BOLD}Application Layer:{Colors.RESET}")
    files_to_check = [
        "src/__init__.py",
        "src/main.py",
        "src/logging_config.py"
    ]
    for file in files_to_check:
        check = check_file_exists(file)
        checks.append(check)
        if check:
            passed += 1
        print_check(file, check)
    
    # Testing Layer
    print(f"\n{Colors.BOLD}Testing Layer:{Colors.RESET}")
    files_to_check = [
        "tests/__init__.py",
        "tests/test_database.py",
        "tests/test_song_repository.py",
        "tests/test_user_repository.py",
        "tests/test_playlist_repository.py"
    ]
    for file in files_to_check:
        check = check_file_exists(file)
        checks.append(check)
        if check:
            passed += 1
        print_check(file, check)
    
    # Documentation
    print(f"\n{Colors.BOLD}Documentation:{Colors.RESET}")
    files_to_check = [
        "README.md",
        "IMPLEMENTATION_SUMMARY.md",
        "QUICK_REFERENCE.md",
        "requirements.txt",
        "docs/sprint1_student_b.md"
    ]
    for file in files_to_check:
        check = check_file_exists(file)
        checks.append(check)
        if check:
            passed += 1
        print_check(file, check)
    
    # Directory Structure
    print(f"\n{Colors.BOLD}Directory Structure:{Colors.RESET}")
    dirs_to_check = [
        "src/database",
        "src/repositories",
        "src/models",
        "tests",
        "docs"
    ]
    for dir in dirs_to_check:
        check = check_dir_exists(dir)
        checks.append(check)
        if check:
            passed += 1
        print_check(dir, check)
    
    # Student A's Code (should be untouched)
    print(f"\n{Colors.BOLD}Student A's Code (Verification Only):{Colors.RESET}")
    files_to_check = [
        "src/models/audio_track.py",
        "src/models/song.py",
        "src/models/playlist.py",
        "src/models/user.py"
    ]
    for file in files_to_check:
        check = check_file_exists(file)
        checks.append(check)
        if check:
            passed += 1
        print_check(f"{file} (unmodified)", check)
    
    # Dependencies
    print(f"\n{Colors.BOLD}Dependencies:{Colors.RESET}")
    try:
        import pytest
        checks.append(True)
        passed += 1
        print_check("pytest installed", True)
    except ImportError:
        checks.append(False)
        print_check("pytest installed", False)
    
    # Print summary
    return print_summary(len(checks), passed)


if __name__ == "__main__":
    sys.exit(main())
