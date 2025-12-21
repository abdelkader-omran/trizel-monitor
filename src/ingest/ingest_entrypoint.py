#!/usr/bin/env python3
"""
src/ingest/ingest_entrypoint.py - RAW Zenodo ingest entrypoint

Implements the AUTO DZ ACT RAW ingest contract for Zenodo records.

CLI:
    python src/ingest/ingest_entrypoint.py --source zenodo --doi <DOI> --mode ingest [--input <path>] [--output-only]

Behavior:
- Offline-first: --input takes precedence
- Writes to: data/raw/<YYYY-MM-DD>/zenodo_<DOI_SUFFIX>/
- Never overwrites: collision => regenerate record_id
- Graceful failures with [ERROR] and [HINT]
"""

import os
import sys
import json
import uuid
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.timestamps import now_utc_iso
from src.utils.hashing import sha256_file, size_bytes
from src.ingest.zenodo_fetch import fetch_zenodo_offline, fetch_zenodo_online


def extract_doi_suffix(doi: str) -> str:
    """
    Extract the numeric suffix from a Zenodo DOI.
    
    Args:
        doi: Full DOI (e.g., "10.5281/zenodo.16292189")
    
    Returns:
        str: Numeric suffix (e.g., "16292189")
    """
    if not doi.startswith("10.5281/zenodo."):
        raise ValueError(f"Invalid Zenodo DOI format: {doi}")
    
    return doi.split("zenodo.")[1]


def generate_record_id() -> str:
    """Generate a unique record ID using UUID v4."""
    return str(uuid.uuid4())


def write_json_atomic(path: str, data: Dict[str, Any]) -> None:
    """
    Write JSON to file atomically.
    
    Args:
        path: Target file path
        data: Data to write
    """
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp_path, path)


def write_raw_record(
    payload_data: Dict[str, Any],
    doi: str,
    provenance: Dict[str, Any],
    output_only: bool = False,
) -> Dict[str, str]:
    """
    Write a RAW Zenodo record according to the immutable contract.
    
    Args:
        payload_data: Zenodo record data to store
        doi: Zenodo DOI
        provenance: Provenance metadata
        output_only: If True, print intended actions without writing
    
    Returns:
        dict: Paths and metadata
    """
    # Determine paths
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    doi_suffix = extract_doi_suffix(doi)
    
    raw_base = Path("data") / "raw" / date_str / f"zenodo_{doi_suffix}"
    records_dir = raw_base / "records"
    payload_dir = raw_base / "payload"
    
    # Generate collision-safe record ID
    max_attempts = 100
    record_id = None
    
    for attempt in range(max_attempts):
        candidate_id = generate_record_id()
        
        record_filename = f"{candidate_id}.json"
        record_path = records_dir / record_filename
        payload_filename = f"{candidate_id}__payload.json"
        payload_path = payload_dir / payload_filename
        
        if not record_path.exists() and not payload_path.exists():
            record_id = candidate_id
            break
    
    if record_id is None:
        raise RuntimeError(f"Failed to generate unique record ID after {max_attempts} attempts")
    
    # Serialize payload
    payload_json = json.dumps(payload_data, indent=2, ensure_ascii=False)
    payload_bytes = payload_json.encode("utf-8")
    
    # Compute integrity metadata
    import hashlib
    sha256_hash = hashlib.sha256(payload_bytes).hexdigest()
    size = len(payload_bytes)
    
    # Dry-run mode
    if output_only:
        print(f"[DRY-RUN] Would create RAW record:")
        print(f"  - Record path: {record_path}")
        print(f"  - Payload path: {payload_path}")
        print(f"  - Record ID: {record_id}")
        print(f"  - SHA256: {sha256_hash}")
        print(f"  - Size: {size} bytes")
        print(f"[DRY-RUN] No files written (dry-run mode)")
        
        return {
            "record_path": str(record_path),
            "payload_path": str(payload_path),
            "record_id": record_id,
        }
    
    # Create directories
    records_dir.mkdir(parents=True, exist_ok=True)
    payload_dir.mkdir(parents=True, exist_ok=True)
    
    # Write payload
    with open(payload_path, "wb") as f:
        f.write(payload_bytes)
    
    # Compute hash from actual file on disk
    actual_sha256 = sha256_file(payload_path)
    actual_size = size_bytes(payload_path)
    
    # Build record metadata
    record_metadata = {
        "record_id": record_id,
        "retrieved_utc": now_utc_iso(),
        "provenance": provenance,
        "sha256": actual_sha256,
        "size_bytes": actual_size,
    }
    
    # Write record
    write_json_atomic(str(record_path), record_metadata)
    
    return {
        "record_path": str(record_path),
        "payload_path": str(payload_path),
        "record_id": record_id,
    }


def main() -> None:
    """Main entrypoint for Zenodo RAW ingest."""
    parser = argparse.ArgumentParser(
        description="AUTO DZ ACT - Zenodo RAW ingest entrypoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        choices=["zenodo"],
        help="Data source (currently only 'zenodo')",
    )
    parser.add_argument(
        "--doi",
        type=str,
        required=True,
        help="Zenodo DOI (e.g., 10.5281/zenodo.16292189)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["ingest"],
        help="Operation mode (currently only 'ingest')",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Offline input file path (offline-first mode)",
    )
    parser.add_argument(
        "--output-only",
        action="store_true",
        help="Dry-run: show intended actions without writing files",
    )
    
    args = parser.parse_args()
    
    try:
        # Fetch data (offline-first)
        if args.input:
            print(f"[INFO] Using offline input: {args.input}")
            data = fetch_zenodo_offline(args.input)
        else:
            print(f"[INFO] Fetching online: {args.doi}")
            data = fetch_zenodo_online(args.doi)
        
        print(f"[OK] Successfully loaded Zenodo record")
        
        # Build provenance
        provenance = {
            "source": "zenodo",
            "doi": args.doi,
            "version": data.get("metadata", {}).get("version", "unknown") if isinstance(data.get("metadata"), dict) else "unknown",
        }
        
        # Write RAW record
        result = write_raw_record(
            payload_data=data,
            doi=args.doi,
            provenance=provenance,
            output_only=args.output_only,
        )
        
        if not args.output_only:
            print(f"[OK] RAW record written:")
            print(f"  - Record: {result['record_path']}")
            print(f"  - Payload: {result['payload_path']}")
            print(f"  - Record ID: {result['record_id']}")
        
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        print(f"[HINT] Check that the file path is correct", file=sys.stderr)
        print(f"[HINT] Use absolute paths or paths relative to current directory", file=sys.stderr)
        sys.exit(1)
    
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        print(f"[HINT] Ensure DOI format is: 10.5281/zenodo.<record_id>", file=sys.stderr)
        print(f"[HINT] Check ZENODO_INDEX.md for valid DOIs", file=sys.stderr)
        sys.exit(1)
    
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in input file: {e}", file=sys.stderr)
        print(f"[HINT] Verify the input file contains valid JSON", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"[ERROR] Ingest failed: {e}", file=sys.stderr)
        print(f"[HINT] Check error message above for details", file=sys.stderr)
        print(f"[HINT] Use --output-only to validate without writing", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
