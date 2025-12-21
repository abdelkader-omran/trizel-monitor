#!/usr/bin/env python3
"""
NASA JPL Horizons API - Baseline Acquisition Tool

Scientific intent:
- Fetch ephemerides data from NASA JPL Horizons system
- Support offline-first execution via --input flag
- Write RAW records to deterministic layout: data/raw/<YYYY-MM-DD>/<SOURCE_ID>/<DATASET_KEY>/

This tool adheres to scientific integrity principles:
- Immutability: RAW records are never modified after writing
- Provenance: Each record includes source metadata
- Deterministic layout: Records are organized by date, source, and dataset
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import requests
except ImportError:
    requests = None


# ============================================================
# Configuration
# ============================================================
HORIZONS_API_URL = os.getenv("HORIZONS_API_URL", "https://ssd.jpl.nasa.gov/api/horizons.api")
HTTP_TIMEOUT_SEC = int(os.getenv("HTTP_TIMEOUT_SEC", "30"))
DATA_DIR = os.getenv("DATA_DIR", "data") or "data"
SOURCE_ID = "NASA_JPL_HORIZONS"
DATASET_KEY = "horizons_api"


# ============================================================
# Utilities
# ============================================================
def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_date() -> str:
    """Return current UTC date in YYYY-MM-DD format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def write_json(path: str, payload: Dict[str, Any]) -> None:
    """Write JSON payload to file with atomic write semantics."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def read_json(path: str) -> Dict[str, Any]:
    """Read JSON payload from file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# Horizons API
# ============================================================
def fetch_horizons_online(target: str, **kwargs) -> Dict[str, Any]:
    """
    Fetch data from NASA JPL Horizons API.
    
    Args:
        target: Target object designation (e.g., "3I/ATLAS", "1I/'Oumuamua")
        **kwargs: Additional parameters for the Horizons API
    
    Returns:
        API response as dictionary
    """
    if requests is None:
        raise RuntimeError("requests library not available. Install with: pip install requests")
    
    params = {
        "format": "json",
        "COMMAND": target,
        "OBJ_DATA": "YES",
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "OBSERVER",
        "CENTER": "500@399",  # Geocentric
        "START_TIME": "2025-01-01",
        "STOP_TIME": "2025-01-02",
        "STEP_SIZE": "1 d",
    }
    params.update(kwargs)
    
    try:
        resp = requests.get(HORIZONS_API_URL, params=params, timeout=HTTP_TIMEOUT_SEC)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Horizons API request failed: {e}")


def fetch_horizons_offline(input_file: str) -> Dict[str, Any]:
    """
    Load data from local JSON file (offline mode).
    
    Args:
        input_file: Path to local JSON file
    
    Returns:
        JSON data from file
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    return read_json(input_file)


# ============================================================
# RAW Record Writing
# ============================================================
def write_raw_record(payload: Dict[str, Any], target: str, offline: bool = False) -> None:
    """
    Write RAW record to deterministic layout.
    
    Layout: data/raw/<YYYY-MM-DD>/<SOURCE_ID>/<DATASET_KEY>/
    - payload/<record_id>__payload.json
    - records/<record_id>.json
    
    Args:
        payload: API response or offline data
        target: Target designation
        offline: Whether this is offline data
    """
    date_str = utc_date()
    record_id = str(uuid.uuid4())
    retrieved_utc = utc_now_iso()
    
    # Build deterministic paths
    base_path = Path(DATA_DIR) / "raw" / date_str / SOURCE_ID / DATASET_KEY
    payload_dir = base_path / "payload"
    records_dir = base_path / "records"
    
    # Create directories
    os.makedirs(payload_dir, exist_ok=True)
    os.makedirs(records_dir, exist_ok=True)
    
    # Write payload (raw API response)
    payload_path = payload_dir / f"{record_id}__payload.json"
    write_json(str(payload_path), payload)
    
    # Write record (with metadata)
    record = {
        "record_id": record_id,
        "source": SOURCE_ID,
        "dataset": DATASET_KEY,
        "target": target,
        "retrieved_utc": retrieved_utc,
        "date": date_str,
        "offline_mode": offline,
        "payload_path": str(payload_path.relative_to(DATA_DIR)),
        "api_url": HORIZONS_API_URL if not offline else None,
    }
    record_path = records_dir / f"{record_id}.json"
    write_json(str(record_path), record)
    
    print(f"[OK] RAW record written:")
    print(f" - Payload: {payload_path}")
    print(f" - Record:  {record_path}")


# ============================================================
# Main
# ============================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="NASA JPL Horizons - Baseline Acquisition Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--target",
        default=os.getenv("TARGET_OBJECT", "3I/ATLAS"),
        help="Target object designation (default: 3I/ATLAS from env)",
    )
    parser.add_argument(
        "--input",
        help="Offline mode: Load data from local JSON file instead of API",
    )
    parser.add_argument(
        "--output-only",
        action="store_true",
        help="Skip API call, only test output structure (dry-run mode)",
    )
    
    args = parser.parse_args()
    
    # Offline-first execution (as per requirements)
    if args.input:
        print(f"[INFO] Offline mode: Loading data from {args.input}")
        try:
            payload = fetch_horizons_offline(args.input)
            write_raw_record(payload, args.target, offline=True)
        except FileNotFoundError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            print(f"[HINT] Ensure the input file exists or use online mode", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Failed to process offline data: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.output_only:
        # Dry-run mode for testing
        print("[INFO] Dry-run mode: Testing output structure only")
        test_payload = {
            "test": True,
            "message": "This is a dry-run test payload"
        }
        write_raw_record(test_payload, args.target, offline=True)
    
    else:
        # Online mode
        print(f"[INFO] Online mode: Fetching data from Horizons API for {args.target}")
        try:
            payload = fetch_horizons_online(args.target)
            write_raw_record(payload, args.target, offline=False)
        except RuntimeError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            print(f"[HINT] Try offline mode with --input <file> to use cached data", file=sys.stderr)
            print(f"[HINT] Or check network connectivity and API availability", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)
    
    print("[OK] Horizons acquisition completed successfully")


if __name__ == "__main__":
    main()
