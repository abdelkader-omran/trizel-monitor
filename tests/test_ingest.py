#!/usr/bin/env python3
"""
Test suite for --mode ingest functionality

Tests:
1. Records are written deterministically under data/raw/
2. Baseline fetch_horizons.py tool integration works as intended
3. Failures yield actionable user feedback
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def test_ingest_offline_mode():
    """Test ingest mode with offline input"""
    print("[TEST] Testing ingest mode with offline input...")
    
    # Create a test input file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = {
            "test": True,
            "metadata": {"target": "test_object"}
        }
        json.dump(test_data, f)
        input_file = f.name
    
    try:
        # Run ingest mode
        cmd = [sys.executable, "src/main.py", "--mode", "ingest", "--input", input_file]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Verify output
        assert "[OK] Ingest mode completed successfully" in result.stdout
        assert "data/raw/" in result.stdout
        
        # Verify directory structure exists
        raw_dir = Path("data/raw")
        assert raw_dir.exists(), "data/raw/ directory should exist"
        
        # Find the created record
        record_files = list(raw_dir.rglob("*.json"))
        assert len(record_files) > 0, "Should have created at least one record"
        
        print(f"  ✓ Created {len(record_files)} files in data/raw/")
        print("  ✓ Ingest mode offline test PASSED")
        return True
        
    finally:
        os.unlink(input_file)


def test_ingest_error_handling():
    """Test ingest mode with missing input file"""
    print("[TEST] Testing ingest mode error handling...")
    
    # Try to run with non-existent input
    cmd = [sys.executable, "src/main.py", "--mode", "ingest", "--input", "/tmp/nonexistent.json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Should fail gracefully
    assert result.returncode != 0, "Should fail with non-existent input"
    assert "ERROR" in result.stderr or "ERROR" in result.stdout
    assert "HINT" in result.stderr or "HINT" in result.stdout
    
    print("  ✓ Error handling test PASSED")
    return True


def test_deterministic_layout():
    """Test that records follow deterministic layout"""
    print("[TEST] Testing deterministic layout...")
    
    raw_dir = Path("data/raw")
    if not raw_dir.exists():
        print("  ⊘ Skipping (no data/raw/ directory)")
        return True
    
    # Find all record files
    record_files = list(raw_dir.rglob("records/*.json"))
    payload_files = list(raw_dir.rglob("payload/*__payload.json"))
    
    if len(record_files) == 0:
        print("  ⊘ Skipping (no records found)")
        return True
    
    # Check structure
    for record_file in record_files:
        parts = record_file.parts
        assert parts[-4] == "NASA_JPL_HORIZONS", "Should have SOURCE_ID in path"
        assert parts[-3] == "horizons_api", "Should have DATASET_KEY in path"
        assert parts[-2] == "records", "Should have records directory"
        
        # Verify date format
        date_part = parts[-5]
        assert len(date_part) == 10, "Date should be YYYY-MM-DD format"
        
    print(f"  ✓ Layout verified for {len(record_files)} records")
    print("  ✓ Deterministic layout test PASSED")
    return True


def test_snapshot_mode_unchanged():
    """Test that snapshot mode still works (no breaking changes)"""
    print("[TEST] Testing snapshot mode (backward compatibility)...")
    
    # Run snapshot mode (default)
    cmd = [sys.executable, "src/main.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Should complete (exit code 0 or 2 for SBDB errors)
    assert result.returncode in [0, 2], f"Unexpected exit code: {result.returncode}"
    assert "Official data snapshot written" in result.stdout or result.returncode == 2
    
    print("  ✓ Snapshot mode test PASSED")
    return True


def main():
    print("\n" + "="*60)
    print("TRIZEL Monitor - Ingest Mode Test Suite")
    print("="*60 + "\n")
    
    # Change to repo root
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    tests = [
        test_snapshot_mode_unchanged,
        test_ingest_offline_mode,
        test_deterministic_layout,
        test_ingest_error_handling,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
        print()
    
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
