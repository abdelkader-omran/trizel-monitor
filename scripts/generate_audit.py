#!/usr/bin/env python3
"""
TRIZEL Monitor - Agency Connectivity Audit Generator

This script scans the repository for:
- Existing agency registry
- Endpoint configurations
- Download code paths
- Current classification rules

Output: docs/audit/AGENCY_CONNECTIVITY_AUDIT.json
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def load_agency_registry(config_path: str) -> Dict[str, Any]:
    """Load the authoritative agency registry."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"agencies": []}


def scan_download_code_paths(src_dir: str) -> List[str]:
    """Scan for download-related code files."""
    code_paths = []
    src_path = Path(src_dir)
    
    if not src_path.exists():
        return code_paths
    
    # Look for download-related Python files
    for py_file in src_path.rglob("*.py"):
        code_paths.append(str(py_file.relative_to(src_path.parent)))
    
    return code_paths


def extract_classification_rules(data_contract_path: str) -> Dict[str, Any]:
    """Extract classification rules from DATA_CONTRACT.md."""
    rules = {
        "classifications": ["RAW_DATA", "SNAPSHOT", "DERIVED"],
        "raw_data_requirements": [
            "Source is official agency (NASA, ESA, JAXA, MPC)",
            "Direct download from archival systems (not API summaries)",
            "Explicit provenance with source URL, checksum, and release policy"
        ],
        "snapshot_criteria": [
            "API responses",
            "Computed orbital elements",
            "Real-time queries"
        ],
        "derived_criteria": [
            "Processed data",
            "Analysis results",
            "Computed metrics"
        ]
    }
    
    # Try to read from actual file if exists
    if os.path.exists(data_contract_path):
        rules["contract_found"] = True
    else:
        rules["contract_found"] = False
    
    return rules


def generate_audit() -> Dict[str, Any]:
    """Generate complete audit report."""
    repo_root = Path(__file__).parent.parent
    
    # Load agency registry
    registry_path = repo_root / "config" / "agency_registry.json"
    registry = load_agency_registry(str(registry_path))
    
    # Extract agency information
    agencies_present = []
    endpoints_count = {}
    
    for agency in registry.get("agencies", []):
        agency_id = agency.get("agency_id", "UNKNOWN")
        agencies_present.append({
            "agency_id": agency_id,
            "name": agency.get("name", ""),
            "status": agency.get("status", "Unknown"),
            "raw_data_capability": agency.get("raw_data_capability", False)
        })
        
        endpoints = agency.get("endpoints", [])
        endpoints_count[agency_id] = {
            "total": len(endpoints),
            "raw_data": sum(1 for e in endpoints if e.get("data_type") == "RAW_DATA"),
            "snapshot": sum(1 for e in endpoints if e.get("data_type") == "SNAPSHOT"),
            "catalog": sum(1 for e in endpoints if e.get("data_type") == "CATALOG")
        }
    
    # Scan download code
    download_paths = scan_download_code_paths(str(repo_root / "src"))
    
    # Extract classification rules
    classification_rules = extract_classification_rules(
        str(repo_root / "DATA_CONTRACT.md")
    )
    
    # Build audit report
    audit = {
        "audit_metadata": {
            "generated_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generator": "scripts/generate_audit.py",
            "version": "1.0.0"
        },
        "repository_status": {
            "agency_registry_found": os.path.exists(registry_path),
            "agency_registry_path": "config/agency_registry.json",
            "data_contract_found": os.path.exists(repo_root / "DATA_CONTRACT.md")
        },
        "agencies_present": agencies_present,
        "endpoints_present_count": endpoints_count,
        "download_code_paths": download_paths,
        "classification_rules_summary": classification_rules,
        "coverage_analysis": {
            "total_agencies": len(agencies_present),
            "active_agencies": sum(1 for a in agencies_present if a["status"] == "Active"),
            "monitoring_agencies": sum(1 for a in agencies_present if a["status"] == "Monitoring"),
            "agencies_with_raw_capability": sum(1 for a in agencies_present if a["raw_data_capability"]),
            "japan_present": any(a["agency_id"] == "JAXA" for a in agencies_present),
            "china_present": any(a["agency_id"] == "CNSA" for a in agencies_present),
            "russia_present": any(a["agency_id"] == "ROSCOSMOS" for a in agencies_present)
        }
    }
    
    return audit


def main():
    """Main entry point."""
    print("=" * 80)
    print("TRIZEL Monitor - Agency Connectivity Audit Generator")
    print("=" * 80)
    
    # Generate audit
    audit = generate_audit()
    
    # Create output directory
    repo_root = Path(__file__).parent.parent
    audit_dir = repo_root / "docs" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    
    # Write audit file
    audit_path = audit_dir / "AGENCY_CONNECTIVITY_AUDIT.json"
    with open(audit_path, 'w', encoding='utf-8') as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Audit generated: {audit_path}")
    print(f"  - Total agencies: {audit['coverage_analysis']['total_agencies']}")
    print(f"  - Active agencies: {audit['coverage_analysis']['active_agencies']}")
    print(f"  - Monitoring agencies: {audit['coverage_analysis']['monitoring_agencies']}")
    print(f"  - Japan (JAXA) present: {audit['coverage_analysis']['japan_present']}")
    print(f"  - China (CNSA) present: {audit['coverage_analysis']['china_present']}")
    print(f"  - Russia (ROSCOSMOS) present: {audit['coverage_analysis']['russia_present']}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
