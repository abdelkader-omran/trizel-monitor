#!/usr/bin/env python3
"""
NASA/JPL Horizons Data Acquisition Tool

Fetches ephemeris and metadata for 3I/ATLAS from the JPL Horizons API.
Produces reproducible, verifiable raw data snapshots with SHA-256 integrity.

Usage:
    # Fetch from API (online mode)
    python tools/fetch_horizons.py

    # Use saved response (offline mode, when API blocked)
    python tools/fetch_horizons.py --input horizons.json
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

try:
    import requests
except ImportError:
    print("ERROR: requests library not found.", file=sys.stderr)
    print("Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# API Configuration
HORIZONS_API_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
TARGET_OBJECT = "3I/ATLAS"

# Deterministic query parameters for reproducibility
# Request ephemeris table for 3I/ATLAS from geocentric observer
CANONICAL_QUERY_PARAMS = {
    "format": "json",
    "COMMAND": "'3I/ATLAS'",
    "OBJ_DATA": "YES",
    "MAKE_EPHEM": "YES",
    "EPHEM_TYPE": "OBSERVER",
    "CENTER": "500@399",  # 500=geocenter, 399=Earth
    "START_TIME": "2025-01-01",
    "STOP_TIME": "2025-01-02",
    "STEP_SIZE": "1d",
    "QUANTITIES": "1,9,20,23,24",  # 1=RA/DEC, 9=mag, 20=range, 23=range-rate, 24=light-time
}


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_timestamp_compact() -> str:
    """Return compact timestamp for filenames (YYYYMMDD_HHMMSS)."""
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def utc_date_iso() -> str:
    """Return current UTC date in YYYY-MM-DD format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 hash of byte data."""
    return hashlib.sha256(data).hexdigest()


def infer_dataset_role(response_text: str) -> str:
    """
    Infer dataset role from Horizons response content.
    
    Returns:
        'ephemeris' if ephemeris data present ($$SOE...$$EOE markers)
        'metadata_only' if only metadata/search results (no ephemeris)
    """
    # Horizons ephemeris tables are marked with $$SOE and $$EOE
    if "$$SOE" in response_text and "$$EOE" in response_text:
        return "ephemeris"
    elif "No matches found" in response_text or "Matching small-bodies" in response_text:
        return "metadata_only"
    else:
        # Default: if it has result data but no clear ephemeris markers
        return "metadata_only"


def fetch_from_api(params: Dict[str, Any], timeout: int = 30) -> Tuple[str, int, Dict[str, str]]:
    """
    Fetch data from Horizons API.
    
    Args:
        params: Query parameters
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (response_text, status_code, headers_dict)
    
    Raises:
        requests.RequestException: On network/HTTP errors
    """
    print(f"Fetching from: {HORIZONS_API_URL}")
    print(f"Query: COMMAND={params.get('COMMAND')}")
    
    response = requests.get(HORIZONS_API_URL, params=params, timeout=timeout)
    response.raise_for_status()
    
    return response.text, response.status_code, dict(response.headers)


def load_from_file(filepath: str) -> str:
    """Load response text from local file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def save_raw_snapshot(content: str, date_dir: str) -> Path:
    """
    Save raw response to timestamped file.
    
    Args:
        content: Raw response text
        date_dir: Date directory (YYYY-MM-DD)
    
    Returns:
        Path to saved file
    """
    raw_dir = Path("data/raw/JPL_HORIZONS") / date_dir
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = utc_timestamp_compact()
    filename = f"horizons_3I_ATLAS_{timestamp}.json"
    filepath = raw_dir / filename
    
    # Write raw content verbatim
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath


def build_raw_record(
    raw_filepath: Path,
    content: str,
    query_params: Dict[str, Any],
    retrieved_utc: str,
    dataset_role: str
) -> Dict[str, Any]:
    """
    Build normalized raw record with integrity and provenance.
    
    Args:
        raw_filepath: Path to raw data file
        content: Raw response content
        query_params: Query parameters used
        retrieved_utc: Retrieval timestamp
        dataset_role: 'ephemeris' or 'metadata_only'
    
    Returns:
        Raw record dictionary
    """
    content_bytes = content.encode('utf-8')
    sha256_hash = compute_sha256(content_bytes)
    size_bytes = len(content_bytes)
    
    # Stable record ID: source + timestamp
    record_id = f"NASA_JPL_HORIZONS__3I_ATLAS__{utc_timestamp_compact()}"
    
    # Use relative path from repository root
    relative_path = str(raw_filepath) if not raw_filepath.is_absolute() else str(raw_filepath.relative_to(Path.cwd()))
    
    record = {
        "record_id": record_id,
        "source": {
            "source_id": "NASA_JPL_HORIZONS",
            "url": HORIZONS_API_URL,
            "endpoint": "horizons.api",
            "description": "NASA/JPL Horizons System - Ephemerides and Observer Tables"
        },
        "acquisition": {
            "retrieved_utc": retrieved_utc,
            "target": TARGET_OBJECT,
            "dataset_role": dataset_role
        },
        "provenance": {
            "command": query_params.get("COMMAND", ""),
            "parameters": {
                k: v for k, v in query_params.items()
                if k not in ["format", "COMMAND"]
            },
            "description": "Canonical fetch with deterministic parameters for reproducibility"
        },
        "integrity": {
            "sha256": sha256_hash,
            "size_bytes": size_bytes
        },
        "raw_data": {
            "relative_path": relative_path,
            "format": "json",
            "content_type": "application/json"
        }
    }
    
    return record


def save_raw_record(record: Dict[str, Any]) -> Path:
    """
    Save raw record to data/records/.
    
    Args:
        record: Raw record dictionary
    
    Returns:
        Path to saved record file
    """
    records_dir = Path("data/records")
    records_dir.mkdir(parents=True, exist_ok=True)
    
    filename = "JPL_HORIZONS__horizons_api.sample.json"
    filepath = records_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    return filepath


def main() -> int:
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Fetch ephemeris data from NASA/JPL Horizons API for 3I/ATLAS',
        epilog='Example: python tools/fetch_horizons.py --input saved_response.json'
    )
    parser.add_argument(
        '--input',
        metavar='FILE',
        help='Use saved response file instead of fetching from API (offline mode)'
    )
    
    args = parser.parse_args()
    
    # Record retrieval timestamp
    retrieved_utc = utc_now_iso()
    date_dir = utc_date_iso()
    
    try:
        if args.input:
            # Offline mode: load from file
            print(f"Loading from file: {args.input}")
            response_content = load_from_file(args.input)
            print(f"Loaded {len(response_content)} bytes")
        else:
            # Online mode: fetch from API
            try:
                response_content, status_code, headers = fetch_from_api(CANONICAL_QUERY_PARAMS)
                print(f"Received {len(response_content)} bytes (HTTP {status_code})")
            except requests.RequestException as e:
                print(f"\nERROR: Failed to fetch from API: {e}", file=sys.stderr)
                print("\nHint: If JPL Horizons API is blocked, use offline mode:", file=sys.stderr)
                print("  python tools/fetch_horizons.py --input horizons.json", file=sys.stderr)
                return 1
        
        # Determine dataset role
        dataset_role = infer_dataset_role(response_content)
        print(f"Dataset role: {dataset_role}")
        
        # Save raw snapshot
        raw_filepath = save_raw_snapshot(response_content, date_dir)
        print(f"Raw snapshot: {raw_filepath}")
        
        # Build raw record
        record = build_raw_record(
            raw_filepath=raw_filepath,
            content=response_content,
            query_params=CANONICAL_QUERY_PARAMS,
            retrieved_utc=retrieved_utc,
            dataset_role=dataset_role
        )
        
        # Save raw record
        record_filepath = save_raw_record(record)
        print(f"Raw record:   {record_filepath}")
        
        # Summary
        print()
        print("=" * 70)
        print("SUCCESS")
        print("=" * 70)
        print(f"Record ID:    {record['record_id']}")
        print(f"Source:       {record['source']['source_id']}")
        print(f"Target:       {record['acquisition']['target']}")
        print(f"Role:         {record['acquisition']['dataset_role']}")
        print(f"SHA-256:      {record['integrity']['sha256']}")
        print(f"Size:         {record['integrity']['size_bytes']} bytes")
        print(f"Retrieved:    {record['acquisition']['retrieved_utc']}")
        print("=" * 70)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"ERROR: File not found: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
