"""
src/ingest/zenodo_fetch.py - Offline-first Zenodo retrieval

Handles fetching Zenodo records with offline-first approach:
- Prioritizes offline input files
- Minimal online fetch with graceful failures
- No DOI inference - only explicit DOIs
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional


def fetch_zenodo_offline(input_path: str) -> Dict[str, Any]:
    """
    Load Zenodo record from offline file.
    
    Args:
        input_path: Path to offline JSON file
    
    Returns:
        dict: Zenodo record data
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file isn't valid JSON
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data


def fetch_zenodo_online(doi: str) -> Dict[str, Any]:
    """
    Fetch Zenodo record via API (minimal online mode).
    
    Args:
        doi: Zenodo DOI (e.g., "10.5281/zenodo.16292189")
    
    Returns:
        dict: Zenodo record data
    
    Raises:
        ImportError: If requests library not available
        Exception: Network or API errors
    
    Note:
        This is a minimal implementation. Network failures emit [ERROR] and [HINT].
    """
    try:
        import requests
    except ImportError:
        print("[ERROR] requests library not available", file=sys.stderr)
        print("[HINT] Install with: pip install requests", file=sys.stderr)
        print("[HINT] Or use --input for offline mode", file=sys.stderr)
        raise
    
    # Extract Zenodo record ID from DOI
    # DOI format: 10.5281/zenodo.<record_id>
    if not doi.startswith("10.5281/zenodo."):
        raise ValueError(f"Invalid Zenodo DOI format: {doi}")
    
    record_id = doi.split("zenodo.")[1]
    url = f"https://zenodo.org/api/records/{record_id}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Network connection failed: {e}", file=sys.stderr)
        print("[HINT] Check internet connectivity", file=sys.stderr)
        print("[HINT] Or use --input for offline mode", file=sys.stderr)
        raise
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out", file=sys.stderr)
        print("[HINT] Try again later or use --input for offline mode", file=sys.stderr)
        raise
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error: {e}", file=sys.stderr)
        print(f"[HINT] Verify DOI is correct: {doi}", file=sys.stderr)
        print("[HINT] Or use --input for offline mode", file=sys.stderr)
        raise


def main() -> None:
    """CLI for Zenodo fetch (testing only)."""
    parser = argparse.ArgumentParser(
        description="Zenodo fetch - offline-first retrieval"
    )
    parser.add_argument(
        "--doi",
        type=str,
        required=True,
        help="Zenodo DOI (e.g., 10.5281/zenodo.16292189)",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Offline input file (optional, takes precedence)",
    )
    
    args = parser.parse_args()
    
    try:
        if args.input:
            print(f"[INFO] Using offline input: {args.input}")
            data = fetch_zenodo_offline(args.input)
        else:
            print(f"[INFO] Fetching online: {args.doi}")
            data = fetch_zenodo_online(args.doi)
        
        print(f"[OK] Successfully loaded record")
        print(f"[OK] Keys: {list(data.keys())[:5]}...")
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
