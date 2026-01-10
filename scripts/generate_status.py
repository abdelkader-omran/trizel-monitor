#!/usr/bin/env python3
"""
TRIZEL Monitor - Agency Connectivity Status Generator

Generates a human-readable Markdown status table from the agency registry.

Output: docs/status/AGENCY_CONNECTIVITY_STATUS.md
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def load_agency_registry(config_path: str) -> Dict[str, Any]:
    """Load the authoritative agency registry."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_status_markdown(registry: Dict[str, Any]) -> str:
    """Generate Markdown status table."""
    
    lines = [
        "# TRIZEL Monitor - Agency Connectivity Status",
        "",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
        f"**Source:** `config/agency_registry.json`",
        "",
        "## Overview",
        "",
        "This document provides the current status of international space agency connectivity",
        "for the TRIZEL Monitor raw data archive system.",
        "",
        "## Status Definitions",
        "",
    ]
    
    # Add status definitions
    status_defs = registry.get("status_definitions", {})
    for status, definition in status_defs.items():
        lines.append(f"- **{status}:** {definition}")
    
    lines.extend([
        "",
        "## Visual Attributes Legend",
        "",
        "| Data Type | Color | Icon | Label |",
        "|-----------|-------|------|-------|",
        "| RAW_DATA | 🟢 Green | ✓ | RAW DATA |",
        "| SNAPSHOT | 🟠 Orange | ⚠ | SNAPSHOT – NO SCIENTIFIC VALUE ALONE |",
        "| DERIVED | 🔵 Blue | → | DERIVED DATA |",
        "",
        "## Agency Status Table",
        "",
        "| Agency | Full Name | Country | Status | Raw Data | Endpoints | Notes |",
        "|--------|-----------|---------|--------|----------|-----------|-------|",
    ])
    
    # Add agency rows
    agencies = registry.get("agencies", [])
    for agency in agencies:
        agency_id = agency.get("agency_id", "")
        name = agency.get("name", "")
        country = agency.get("country", "")
        status = agency.get("status", "Unknown")
        raw_capability = "✓" if agency.get("raw_data_capability", False) else "✗"
        endpoint_count = len(agency.get("endpoints", []))
        notes = agency.get("status_notes", "")
        
        # Status emoji
        status_emoji = {
            "Active": "🟢",
            "Monitoring": "🟡",
            "Limited": "🔴"
        }.get(status, "⚪")
        
        lines.append(
            f"| {agency_id} | {name} | {country} | {status_emoji} {status} | "
            f"{raw_capability} | {endpoint_count} | {notes} |"
        )
    
    lines.extend([
        "",
        "## Detailed Endpoint Information",
        "",
    ])
    
    # Add detailed endpoint information for each agency
    for agency in agencies:
        agency_id = agency.get("agency_id", "")
        name = agency.get("name", "")
        endpoints = agency.get("endpoints", [])
        
        lines.extend([
            f"### {agency_id} - {name}",
            "",
        ])
        
        if not endpoints:
            lines.append("*No endpoints configured.*")
            lines.append("")
            continue
        
        lines.extend([
            "| Endpoint | Type | URL | Auth Required | Download Mode |",
            "|----------|------|-----|---------------|---------------|",
        ])
        
        for endpoint in endpoints:
            endpoint_name = endpoint.get("name", "")
            data_type = endpoint.get("data_type", "")
            url = endpoint.get("url", "")
            requires_auth = "Yes" if endpoint.get("requires_auth", False) else "No"
            download_mode = endpoint.get("download_mode", "")
            
            # Data type with emoji
            type_emoji = {
                "RAW_DATA": "🟢",
                "SNAPSHOT": "🟠",
                "CATALOG": "📋",
                "DERIVED": "🔵"
            }.get(data_type, "⚪")
            
            lines.append(
                f"| {endpoint_name} | {type_emoji} {data_type} | {url} | "
                f"{requires_auth} | {download_mode} |"
            )
        
        lines.append("")
    
    lines.extend([
        "## Implementation Status",
        "",
        "### Coverage Summary",
        "",
    ])
    
    # Calculate coverage statistics
    total_agencies = len(agencies)
    active_agencies = sum(1 for a in agencies if a.get("status") == "Active")
    monitoring_agencies = sum(1 for a in agencies if a.get("status") == "Monitoring")
    raw_capable = sum(1 for a in agencies if a.get("raw_data_capability", False))
    
    lines.extend([
        f"- **Total Agencies:** {total_agencies}",
        f"- **Active (with raw data access):** {active_agencies}",
        f"- **Monitoring (limited access):** {monitoring_agencies}",
        f"- **Agencies with raw data capability:** {raw_capable}",
        "",
        "### Required Coverage Verification",
        "",
    ])
    
    # Verify required agencies
    required = {
        "Japan (JAXA)": any(a.get("agency_id") == "JAXA" for a in agencies),
        "China (CNSA)": any(a.get("agency_id") == "CNSA" for a in agencies),
        "Russia (ROSCOSMOS)": any(a.get("agency_id") == "ROSCOSMOS" for a in agencies)
    }
    
    for country, present in required.items():
        status_icon = "✓" if present else "✗"
        lines.append(f"- {status_icon} **{country}:** {'Present' if present else 'Missing'}")
    
    lines.extend([
        "",
        "---",
        "",
        "*This document is automatically generated from the authoritative agency registry.*  ",
        "*Last update: " + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC') + "*",
        ""
    ])
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    print("=" * 80)
    print("TRIZEL Monitor - Agency Connectivity Status Generator")
    print("=" * 80)
    
    repo_root = Path(__file__).parent.parent
    
    # Load registry
    registry_path = repo_root / "config" / "agency_registry.json"
    if not registry_path.exists():
        print(f"ERROR: Agency registry not found at {registry_path}")
        return 1
    
    registry = load_agency_registry(str(registry_path))
    
    # Generate markdown
    markdown = generate_status_markdown(registry)
    
    # Create output directory
    status_dir = repo_root / "docs" / "status"
    status_dir.mkdir(parents=True, exist_ok=True)
    
    # Write status file
    status_path = status_dir / "AGENCY_CONNECTIVITY_STATUS.md"
    with open(status_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"\n✓ Status document generated: {status_path}")
    print(f"  - Total agencies: {len(registry.get('agencies', []))}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
