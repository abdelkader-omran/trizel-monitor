#!/usr/bin/env python3
"""
Minimal tests for Phase 2 ingest mode.

Tests cover:
1. Offline ingest creates RAW path segments
2. Record JSON contains required fields
3. Ingest failure emits [ERROR] and [HINT]
4. Snapshot mode still works (smoke test)
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return result."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=get_repo_root(),
    )
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    return result


def get_repo_root():
    """Get repository root directory."""
    return Path(__file__).parent.parent


def test_offline_ingest_creates_raw_paths():
    """Test that offline ingest creates correct RAW directory structure."""
    print("[TEST] Offline ingest creates RAW path segments...")
    
    repo_root = get_repo_root()
    
    # Create test input file
    test_data = {
        "metadata": {"test": "data"},
        "payload": {"sample": "content"},
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name
    
    try:
        # Run ingest
        cmd = [
            sys.executable,
            str(repo_root / "src" / "main.py"),
            "--mode", "ingest",
            "--input", temp_file,
        ]
        result = run_command(cmd)
        
        # Find the RAW directory that was created (should be today's date)
        raw_dir = repo_root / "data" / "raw"
        assert raw_dir.exists(), "RAW directory not created"
        
        # Check structure: data/raw/<date>/horizons/snapshot/
        date_dirs = [d for d in raw_dir.iterdir() if d.is_dir()]
        assert len(date_dirs) > 0, "No date directory created"
        
        # Check for horizons/snapshot structure
        date_dir = date_dirs[0]
        horizons_dir = date_dir / "horizons" / "snapshot"
        assert horizons_dir.exists(), "horizons/snapshot directory not created"
        
        # Check for records and payload directories
        records_dir = horizons_dir / "records"
        payload_dir = horizons_dir / "payload"
        assert records_dir.exists(), "records directory not created"
        assert payload_dir.exists(), "payload directory not created"
        
        print("[PASS] RAW path segments created correctly")
        
    finally:
        os.unlink(temp_file)


def test_record_json_contains_required_fields():
    """Test that record JSON contains all required fields."""
    print("[TEST] Record JSON contains required fields...")
    
    repo_root = get_repo_root()
    
    # Create test input file
    test_data = {"test": "data"}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name
    
    try:
        # Run ingest
        cmd = [
            sys.executable,
            str(repo_root / "src" / "main.py"),
            "--mode", "ingest",
            "--input", temp_file,
        ]
        result = run_command(cmd)
        
        # Find the record file
        raw_dir = repo_root / "data" / "raw"
        record_files = list(raw_dir.glob("**/records/*.json"))
        assert len(record_files) > 0, "No record files created"
        
        # Read the most recent record
        record_file = max(record_files, key=lambda p: p.stat().st_mtime)
        with open(record_file) as f:
            record = json.load(f)
        
        # Check required fields
        required_fields = [
            "record_id",
            "retrieved_utc",
            "provenance",
            "sha256",
            "size_bytes",
            "payload_path",
        ]
        
        for field in required_fields:
            assert field in record, f"Missing required field: {field}"
        
        # Validate field types
        assert isinstance(record["record_id"], str), "record_id must be string"
        assert isinstance(record["retrieved_utc"], str), "retrieved_utc must be string"
        assert isinstance(record["provenance"], dict), "provenance must be dict"
        assert isinstance(record["sha256"], str), "sha256 must be string"
        assert isinstance(record["size_bytes"], int), "size_bytes must be int"
        assert isinstance(record["payload_path"], str), "payload_path must be string"
        
        print("[PASS] Record JSON has all required fields with correct types")
        
    finally:
        os.unlink(temp_file)


def test_ingest_failure_emits_error_and_hint():
    """Test that ingest failures emit [ERROR] and [HINT] messages."""
    print("[TEST] Ingest failure emits [ERROR] and [HINT]...")
    
    repo_root = get_repo_root()
    
    # Run ingest with non-existent file
    cmd = [
        sys.executable,
        str(repo_root / "src" / "main.py"),
        "--mode", "ingest",
        "--input", "/nonexistent/file.json",
    ]
    result = run_command(cmd, check=False)
    
    # Should have non-zero exit code
    assert result.returncode != 0, "Should fail with non-zero exit code"
    
    # Should have [ERROR] message
    assert "[ERROR]" in result.stderr, "Should emit [ERROR] message"
    
    # Should have [HINT] message
    assert "[HINT]" in result.stderr, "Should emit [HINT] message"
    
    print("[PASS] Ingest failure emits [ERROR] and [HINT]")


def test_snapshot_mode_still_works():
    """Smoke test that snapshot mode still works."""
    print("[TEST] Snapshot mode still works (smoke test)...")
    
    repo_root = get_repo_root()
    
    # Run snapshot mode
    cmd = [
        sys.executable,
        str(repo_root / "src" / "main.py"),
    ]
    result = run_command(cmd, check=False)
    
    # May exit with 2 if network is unavailable, which is OK
    assert result.returncode in [0, 2], f"Unexpected exit code: {result.returncode}"
    
    # Should produce output
    assert "[OK]" in result.stdout or "[ERROR]" in result.stderr, "Should produce output"
    
    print("[PASS] Snapshot mode runs")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Running minimal ingest tests")
    print("=" * 60)
    
    tests = [
        test_offline_ingest_creates_raw_paths,
        test_record_json_contains_required_fields,
        test_ingest_failure_emits_error_and_hint,
        test_snapshot_mode_still_works,
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
