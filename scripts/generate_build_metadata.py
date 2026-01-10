#!/usr/bin/env python3
"""
TRIZEL Monitor - Build Metadata Generator

Generates build.json with factual system status information:
- Build hash
- Deploy timestamp
- RAW data count
- Snapshot count
- Active agencies count
- Last update timestamps
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def get_git_commit_hash() -> str:
    """Get current git commit hash."""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def count_raw_data_files(raw_dir: Path) -> Dict[str, Any]:
    """Count RAW data files by agency."""
    if not raw_dir.exists():
        return {"total": 0, "by_agency": {}}
    
    by_agency = {}
    total = 0
    
    for agency_dir in raw_dir.iterdir():
        if agency_dir.is_dir():
            # Count files (excluding .meta.json sidecar files)
            files = [
                f for f in agency_dir.rglob("*")
                if f.is_file() and not f.name.endswith('.meta.json')
            ]
            by_agency[agency_dir.name] = len(files)
            total += len(files)
    
    return {"total": total, "by_agency": by_agency}


def count_snapshot_files(snapshot_dir: Path) -> int:
    """Count snapshot files."""
    if not snapshot_dir.exists():
        return 0
    
    return len([f for f in snapshot_dir.glob("*.json") if f.is_file()])


def count_active_agencies(registry_path: Path) -> Dict[str, int]:
    """Count agencies by status."""
    if not registry_path.exists():
        return {"active": 0, "monitoring": 0, "limited": 0, "total": 0}
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    agencies = registry.get("agencies", [])
    counts = {
        "active": sum(1 for a in agencies if a.get("status") == "Active"),
        "monitoring": sum(1 for a in agencies if a.get("status") == "Monitoring"),
        "limited": sum(1 for a in agencies if a.get("status") == "Limited"),
        "total": len(agencies)
    }
    
    return counts


def get_last_raw_update(raw_dir: Path) -> str:
    """Get timestamp of most recent RAW data file."""
    if not raw_dir.exists():
        return "never"
    
    latest_mtime = 0
    
    for f in raw_dir.rglob("*"):
        if f.is_file() and not f.name.endswith('.meta.json'):
            mtime = f.stat().st_mtime
            if mtime > latest_mtime:
                latest_mtime = mtime
    
    if latest_mtime == 0:
        return "never"
    
    return datetime.utcfromtimestamp(latest_mtime).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_last_snapshot_update(snapshot_dir: Path) -> str:
    """Get timestamp of most recent snapshot file."""
    if not snapshot_dir.exists():
        return "never"
    
    latest_mtime = 0
    
    for f in snapshot_dir.glob("*.json"):
        if f.is_file():
            mtime = f.stat().st_mtime
            if mtime > latest_mtime:
                latest_mtime = mtime
    
    if latest_mtime == 0:
        return "never"
    
    return datetime.utcfromtimestamp(latest_mtime).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_build_metadata() -> Dict[str, Any]:
    """Generate complete build metadata."""
    repo_root = Path(__file__).parent.parent
    
    raw_dir = repo_root / "data" / "raw"
    snapshot_dir = repo_root / "data"
    registry_path = repo_root / "config" / "agency_registry.json"
    
    raw_data_counts = count_raw_data_files(raw_dir)
    snapshot_count = count_snapshot_files(snapshot_dir)
    agency_counts = count_active_agencies(registry_path)
    
    metadata = {
        "build_metadata": {
            "version": "3.0.0",
            "build_hash": get_git_commit_hash(),
            "deploy_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generator": "scripts/generate_build_metadata.py",
            "schema_version": "1.0.0"
        },
        "data_counts": {
            "raw_data_total": raw_data_counts["total"],
            "raw_data_by_agency": raw_data_counts["by_agency"],
            "snapshot_total": snapshot_count
        },
        "agency_counts": agency_counts,
        "last_updates": {
            "last_raw_update_utc": get_last_raw_update(raw_dir),
            "last_snapshot_update_utc": get_last_snapshot_update(snapshot_dir)
        },
        "system_status": {
            "automation": "Active",
            "data_governance_version": "3.0.0",
            "validation": "Enforced via CI"
        }
    }
    
    return metadata


def main():
    """Main entry point."""
    print("=" * 80)
    print("TRIZEL Monitor - Build Metadata Generator")
    print("=" * 80)
    print()
    
    # Generate metadata
    metadata = generate_build_metadata()
    
    # Create output directory
    repo_root = Path(__file__).parent.parent
    site_dir = repo_root / "site"
    site_dir.mkdir(parents=True, exist_ok=True)
    
    # Write build.json
    build_path = site_dir / "build.json"
    with open(build_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Build metadata generated: {build_path}")
    print(f"  - Build hash: {metadata['build_metadata']['build_hash']}")
    print(f"  - RAW data files: {metadata['data_counts']['raw_data_total']}")
    print(f"  - Snapshot files: {metadata['data_counts']['snapshot_total']}")
    print(f"  - Active agencies: {metadata['agency_counts']['active']}")
    print(f"  - Total agencies: {metadata['agency_counts']['total']}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
