#!/usr/bin/env python3
"""
Fetch data from NASA/JPL Horizons API for 3I/ATLAS

This tool performs a reproducible fetch from the Horizons API and stores:
1. Raw response in data/raw/JPL_HORIZONS/<YYYY-MM-DD>/horizons_<query_id>.json
2. Schema-compliant raw record in data/records/JPL_HORIZONS__horizons_api.sample.json

Requirements:
- Deterministic request parameters
- SHA-256 hash computation
- UTC timestamps in ISO-8601 format
- Full compliance with spec/raw_record.schema.json
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

try:
    import requests
except ImportError:
    print("ERROR: requests library not found. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# Configuration
HORIZONS_API_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
TARGET_OBJECT = "3I/ATLAS"
SOURCE_ID = "JPL_HORIZONS"
ENDPOINT_ID = "horizons_api"

# Query parameters (deterministic)
# Request ephemeris data for 3I/ATLAS
DEFAULT_QUERY_PARAMS = {
    "format": "json",
    "COMMAND": "'3I/ATLAS'",  # Target object
    "OBJ_DATA": "YES",  # Include object data
    "MAKE_EPHEM": "YES",  # Generate ephemeris
    "EPHEM_TYPE": "OBSERVER",  # Observer table
    "CENTER": "500@399",  # Geocentric (Earth center)
    "START_TIME": "2025-01-01",  # Fixed start time for reproducibility
    "STOP_TIME": "2025-01-02",  # Fixed stop time
    "STEP_SIZE": "1d",  # 1 day step
    "QUANTITIES": "1,9,20,23,24",  # Specific quantities for reproducibility
}


def utc_now_iso() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_date_compact() -> str:
    """Return current UTC date in YYYY-MM-DD format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 hash of data."""
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()


def fetch_from_horizons(params: Dict[str, Any], timeout: int = 30) -> tuple:
    """
    Fetch data from Horizons API.
    
    Returns:
        tuple: (response_text, status_code, headers)
    
    Raises:
        requests.RequestException: On network errors
    """
    print(f"Fetching from: {HORIZONS_API_URL}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    response = requests.get(HORIZONS_API_URL, params=params, timeout=timeout)
    response.raise_for_status()
    
    return response.text, response.status_code, dict(response.headers)


def save_raw_response(response_text: str, query_id: str) -> Path:
    """
    Save raw response to file.
    
    Args:
        response_text: Raw response text
        query_id: Identifier for this query
    
    Returns:
        Path to saved file
    """
    date_str = utc_date_compact()
    raw_dir = Path("data/raw/JPL_HORIZONS") / date_str
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"horizons_{query_id}.json"
    filepath = raw_dir / filename
    
    # Write raw response
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(response_text)
    
    print(f"Raw response saved to: {filepath}")
    return filepath


def create_raw_record(
    raw_file_path: Path,
    response_text: str,
    query_params: Dict[str, Any],
    retrieved_utc: str,
    status_code: int,
    headers: Dict[str, str]
) -> Dict[str, Any]:
    """
    Create a schema-compliant raw record.
    
    Args:
        raw_file_path: Path to the raw data file
        response_text: Raw response text
        query_params: Query parameters used
        retrieved_utc: UTC timestamp of retrieval
        status_code: HTTP status code
        headers: HTTP response headers
    
    Returns:
        Raw record dictionary
    """
    # Compute integrity information
    response_bytes = response_text.encode('utf-8')
    sha256_hash = compute_sha256(response_bytes)
    file_size = len(response_bytes)
    
    # Get relative path from repository root
    relative_path = str(raw_file_path)
    
    # Create record
    record = {
        "record_version": "1.0",
        "source": {
            "source_id": SOURCE_ID,
            "endpoint_id": ENDPOINT_ID,
            "endpoint_url": HORIZONS_API_URL
        },
        "acquisition": {
            "retrieved_utc": retrieved_utc,
            "query_parameters": query_params,
            "http_status": status_code,
            "response_headers": {
                "content-type": headers.get("Content-Type", ""),
                "date": headers.get("Date", "")
            }
        },
        "integrity": {
            "sha256": sha256_hash,
            "size_bytes": file_size
        },
        "raw_data_ref": {
            "relative_path": relative_path,
            "format": "json"
        },
        "metadata": {
            "target": TARGET_OBJECT,
            "notes": "Canonical fetch for 3I/ATLAS from JPL Horizons API"
        }
    }
    
    return record


def save_raw_record(record: Dict[str, Any]) -> Path:
    """
    Save raw record to file.
    
    Args:
        record: Raw record dictionary
    
    Returns:
        Path to saved record file
    """
    records_dir = Path("data/records")
    records_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{SOURCE_ID}__{ENDPOINT_ID}.sample.json"
    filepath = records_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add trailing newline
    
    print(f"Raw record saved to: {filepath}")
    return filepath


def load_local_file(input_path: str) -> str:
    """
    Load a local JSON file (for --input option).
    
    Args:
        input_path: Path to local JSON file
    
    Returns:
        File contents as string
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Fetch data from NASA/JPL Horizons API for 3I/ATLAS'
    )
    parser.add_argument(
        '--input',
        metavar='FILE',
        help='Use local JSON file instead of fetching from API (for reproducibility when API is blocked)'
    )
    parser.add_argument(
        '--query-id',
        default='3I_ATLAS',
        help='Query identifier for filename (default: 3I_ATLAS)'
    )
    
    args = parser.parse_args()
    
    # Record retrieval timestamp
    retrieved_utc = utc_now_iso()
    
    # Query parameters
    query_params = DEFAULT_QUERY_PARAMS.copy()
    
    try:
        if args.input:
            # Load from local file
            print(f"Loading from local file: {args.input}")
            response_text = load_local_file(args.input)
            status_code = 200
            headers = {
                "Content-Type": "application/json",
                "Date": retrieved_utc
            }
            print(f"Loaded {len(response_text)} bytes from local file")
        else:
            # Fetch from API
            response_text, status_code, headers = fetch_from_horizons(query_params)
            print(f"Received {len(response_text)} bytes from API")
        
        # Save raw response
        raw_file_path = save_raw_response(response_text, args.query_id)
        
        # Create raw record
        record = create_raw_record(
            raw_file_path=raw_file_path,
            response_text=response_text,
            query_params=query_params,
            retrieved_utc=retrieved_utc,
            status_code=status_code,
            headers=headers
        )
        
        # Save raw record
        record_file_path = save_raw_record(record)
        
        print()
        print("=" * 60)
        print("SUCCESS: Data acquisition complete")
        print("=" * 60)
        print(f"Raw data: {raw_file_path}")
        print(f"Record:   {record_file_path}")
        print(f"SHA-256:  {record['integrity']['sha256']}")
        print(f"Size:     {record['integrity']['size_bytes']} bytes")
        print()
        print("To validate, run:")
        print(f"  python tools/validate_raw_record.py {record_file_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"ERROR: File not found: {e}", file=sys.stderr)
        return 1
    except requests.RequestException as e:
        print(f"ERROR: Network request failed: {e}", file=sys.stderr)
        print()
        print("Hint: If API is blocked, save a response locally and use:")
        print("  python tools/fetch_horizons.py --input horizons.json")
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
