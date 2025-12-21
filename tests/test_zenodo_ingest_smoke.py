#!/usr/bin/env python3
"""
tests/test_zenodo_ingest_smoke.py - Minimal offline Zenodo ingest smoke test

Tests the basic functionality of Zenodo RAW ingest without heavy dependencies.
Uses a small local fixture JSON as --input for offline testing.
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path


def get_repo_root():
    """Get repository root directory."""
    return Path(__file__).parent.parent


def test_zenodo_ingest_offline_smoke():
    """
    Smoke test: offline Zenodo ingest with fixture data.
    
    Verifies:
    1. CLI accepts required arguments
    2. Offline mode works with --input
    3. Record schema contains all required keys
    4. Output structure matches contract
    """
    print("[TEST] Zenodo ingest offline smoke test...")
    
    repo_root = get_repo_root()
    
    # Create minimal test fixture
    fixture_data = {
        "metadata": {
            "title": "Test Zenodo Record",
            "version": "1.0",
        },
        "id": "12345",
        "doi": "10.5281/zenodo.12345",
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(fixture_data, f)
        temp_file = f.name
    
    try:
        # Run ingest command
        cmd = [
            sys.executable,
            str(repo_root / "src" / "ingest" / "ingest_entrypoint.py"),
            "--source", "zenodo",
            "--doi", "10.5281/zenodo.16292189",
            "--mode", "ingest",
            "--input", temp_file,
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
        
        # Check success
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "[OK]" in result.stdout, "Expected [OK] in output"
        
        # Find the created record
        raw_dir = repo_root / "data" / "raw"
        assert raw_dir.exists(), "RAW directory not created"
        
        # Find Zenodo records
        record_files = list(raw_dir.glob("**/zenodo_*/records/*.json"))
        assert len(record_files) > 0, "No record files created"
        
        # Read most recent record
        record_file = max(record_files, key=lambda p: p.stat().st_mtime)
        with open(record_file) as f:
            record = json.load(f)
        
        # Verify required fields
        required_fields = [
            "record_id",
            "retrieved_utc",
            "provenance",
            "sha256",
            "size_bytes",
        ]
        
        for field in required_fields:
            assert field in record, f"Missing required field: {field}"
        
        # Verify provenance structure
        assert "source" in record["provenance"], "Missing provenance.source"
        assert record["provenance"]["source"] == "zenodo", "Invalid provenance.source"
        assert "doi" in record["provenance"], "Missing provenance.doi"
        assert "version" in record["provenance"], "Missing provenance.version"
        
        # Verify field types
        assert isinstance(record["record_id"], str), "record_id must be string"
        assert isinstance(record["retrieved_utc"], str), "retrieved_utc must be string"
        assert "+00:00" in record["retrieved_utc"], "retrieved_utc must be timezone-aware"
        assert isinstance(record["sha256"], str), "sha256 must be string"
        assert len(record["sha256"]) == 64, "sha256 must be 64 hex chars"
        assert isinstance(record["size_bytes"], int), "size_bytes must be int"
        
        print("[PASS] Zenodo ingest offline smoke test")
        
    finally:
        os.unlink(temp_file)


def test_zenodo_ingest_output_only():
    """
    Test --output-only (dry-run) mode.
    
    Verifies:
    1. No files are created
    2. Output shows intended actions
    3. Exit code is 0
    """
    print("[TEST] Zenodo ingest output-only mode...")
    
    repo_root = get_repo_root()
    
    # Create minimal test fixture
    fixture_data = {"test": "data"}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(fixture_data, f)
        temp_file = f.name
    
    try:
        # Count existing files before
        raw_dir = repo_root / "data" / "raw"
        if raw_dir.exists():
            before_count = len(list(raw_dir.glob("**/zenodo_*/records/*.json")))
        else:
            before_count = 0
        
        # Run with --output-only
        cmd = [
            sys.executable,
            str(repo_root / "src" / "ingest" / "ingest_entrypoint.py"),
            "--source", "zenodo",
            "--doi", "10.5281/zenodo.16292189",
            "--mode", "ingest",
            "--input", temp_file,
            "--output-only",
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
        
        # Check success and dry-run indicators
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "[DRY-RUN]" in result.stdout, "Expected [DRY-RUN] in output"
        assert "Would create RAW record" in result.stdout, "Expected dry-run description"
        
        # Verify no new files created
        if raw_dir.exists():
            after_count = len(list(raw_dir.glob("**/zenodo_*/records/*.json")))
        else:
            after_count = 0
        
        assert after_count == before_count, "Files were created in dry-run mode"
        
        print("[PASS] Zenodo ingest output-only mode")
        
    finally:
        os.unlink(temp_file)


def test_zenodo_ingest_error_handling():
    """
    Test graceful error handling.
    
    Verifies:
    1. Non-existent file produces [ERROR] and [HINT]
    2. Exit code is non-zero
    """
    print("[TEST] Zenodo ingest error handling...")
    
    repo_root = get_repo_root()
    
    # Run with non-existent file
    cmd = [
        sys.executable,
        str(repo_root / "src" / "ingest" / "ingest_entrypoint.py"),
        "--source", "zenodo",
        "--doi", "10.5281/zenodo.16292189",
        "--mode", "ingest",
        "--input", "/nonexistent/file.json",
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(repo_root),
    )
    
    # Check failure indicators
    assert result.returncode != 0, "Should fail with non-zero exit code"
    assert "[ERROR]" in result.stderr, "Should emit [ERROR] message"
    assert "[HINT]" in result.stderr, "Should emit [HINT] message"
    
    print("[PASS] Zenodo ingest error handling")


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("Running Zenodo ingest smoke tests")
    print("=" * 60)
    
    tests = [
        test_zenodo_ingest_offline_smoke,
        test_zenodo_ingest_output_only,
        test_zenodo_ingest_error_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Tests: {passed} passed, {failed} failed")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
