#!/usr/bin/env python3
"""
tools/fetch_horizons.py - Offline-first Horizons data ingestion

This tool processes offline Horizons API responses and prepares them
for the RAW data layer according to the immutable RAW writer contract.
"""

import os
import sys
import json
import hashlib
import argparse
import uuid
from datetime import datetime, timezone
from typing import Any, Dict


def compute_sha256(data: bytes) -> str:
    """Compute SHA256 hash of data."""
    return hashlib.sha256(data).hexdigest()


def utc_now_iso() -> str:
    """Return current UTC time in ISO-8601 format with timezone."""
    return datetime.now(timezone.utc).isoformat()


def write_json(path: str, payload: Dict[str, Any]) -> None:
    """Write JSON to file atomically."""
    # Write to temp file first, then rename (atomic on POSIX)
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    os.replace(temp_path, path)


def generate_record_id() -> str:
    """Generate a unique record ID."""
    return str(uuid.uuid4())


def write_raw_record(
    payload_data: Dict[str, Any],
    source_id: str,
    dataset_key: str,
    provenance: Dict[str, Any],
) -> Dict[str, str]:
    """
    Write a RAW record according to the immutable contract.
    
    Returns dict with paths written.
    """
    # Determine date-based directory
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    
    # RAW base path
    raw_base = os.path.join("data", "raw", date_str, source_id, dataset_key)
    records_dir = os.path.join(raw_base, "records")
    payload_dir = os.path.join(raw_base, "payload")
    
    # Create directories
    os.makedirs(records_dir, exist_ok=True)
    os.makedirs(payload_dir, exist_ok=True)
    
    # Generate record ID with collision detection
    max_attempts = 100
    record_id = None
    for attempt in range(max_attempts):
        candidate_id = generate_record_id()
        
        # Check if this ID already exists
        record_filename = f"{candidate_id}.json"
        record_path = os.path.join(records_dir, record_filename)
        payload_filename = f"{candidate_id}__payload.json"
        payload_path = os.path.join(payload_dir, payload_filename)
        
        if not os.path.exists(record_path) and not os.path.exists(payload_path):
            record_id = candidate_id
            break
    
    if record_id is None:
        raise RuntimeError(f"Failed to generate unique record ID after {max_attempts} attempts")
    
    # Serialize payload to JSON bytes
    payload_json = json.dumps(payload_data, indent=2, ensure_ascii=False)
    payload_bytes = payload_json.encode("utf-8")
    
    # Compute integrity metadata
    sha256_hash = compute_sha256(payload_bytes)
    size_bytes = len(payload_bytes)
    
    # Write payload file (using the collision-safe paths)
    with open(payload_path, "wb") as f:
        f.write(payload_bytes)
    
    # Build record metadata
    record_metadata = {
        "record_id": record_id,
        "retrieved_utc": utc_now_iso(),
        "provenance": provenance,
        "sha256": sha256_hash,
        "size_bytes": size_bytes,
        "payload_path": os.path.join("payload", payload_filename),
    }
    
    # Write record file
    write_json(record_path, record_metadata)
    
    return {
        "record_path": record_path,
        "payload_path": payload_path,
        "record_id": record_id,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch Horizons - Offline-first data ingestion",
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to offline Horizons JSON file",
    )
    parser.add_argument(
        "--output-only",
        action="store_true",
        help="Dry-run mode: show intended actions without writing files",
    )

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Read and validate JSON
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to read input file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[OK] Successfully read input file: {args.input}")
    
    # Build provenance
    provenance = {
        "source": "offline_file",
        "input_file": os.path.abspath(args.input),
        "ingested_at": utc_now_iso(),
    }
    
    # For now, use "horizons" as source_id and "snapshot" as dataset_key
    # These could be extracted from metadata or made configurable
    source_id = "horizons"
    dataset_key = "snapshot"
    
    # Dry-run mode
    if args.output_only:
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        raw_base = os.path.join("data", "raw", date_str, source_id, dataset_key)
        
        # Simulate record ID generation
        record_id = generate_record_id()
        record_path = os.path.join(raw_base, "records", f"{record_id}.json")
        payload_path = os.path.join(raw_base, "payload", f"{record_id}__payload.json")
        
        # Compute what would be written
        payload_json = json.dumps(data, indent=2, ensure_ascii=False)
        payload_bytes = payload_json.encode("utf-8")
        sha256_hash = compute_sha256(payload_bytes)
        size_bytes = len(payload_bytes)
        
        print(f"[DRY-RUN] Would create RAW record:")
        print(f"  - Record path: {record_path}")
        print(f"  - Payload path: {payload_path}")
        print(f"  - Record ID: {record_id}")
        print(f"  - SHA256: {sha256_hash}")
        print(f"  - Size: {size_bytes} bytes")
        print(f"[DRY-RUN] No files written (dry-run mode)")
        sys.exit(0)
    
    try:
        # Write RAW record
        result = write_raw_record(
            payload_data=data,
            source_id=source_id,
            dataset_key=dataset_key,
            provenance=provenance,
        )
        
        print(f"[OK] RAW record written:")

        print(f"  - Record: {result['record_path']}")
        print(f"  - Payload: {result['payload_path']}")
        print(f"  - Record ID: {result['record_id']}")
        
    except Exception as e:
        print(f"[ERROR] Failed to write RAW record: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
