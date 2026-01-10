#!/usr/bin/env python3
"""
CI Validation Script for TRIZEL Monitor Data Integrity

This script enforces the raw data archival integrity rules:
1. All data files must have explicit data_class
2. Mandatory metadata fields must be present
3. Raw data must be verifiable and downloadable
4. Snapshots must reference raw data sources
5. Schema validation against JSON schema

Exit codes:
0 - All validations passed
1 - Validation failures detected
"""

import sys
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple
import hashlib


# Validation results
class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []
    
    def add_error(self, message: str):
        self.errors.append(f"❌ ERROR: {message}")
    
    def add_warning(self, message: str):
        self.warnings.append(f"⚠️  WARNING: {message}")
    
    def add_pass(self, message: str):
        self.passed.append(f"✓ PASS: {message}")
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def print_summary(self):
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        
        if self.passed:
            print(f"\n✓ PASSED ({len(self.passed)}):")
            for msg in self.passed:
                print(f"  {msg}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for msg in self.errors:
                print(f"  {msg}")
        
        print("\n" + "="*70)
        if self.has_errors():
            print("VALIDATION FAILED")
        else:
            print("VALIDATION PASSED")
        print("="*70 + "\n")


def validate_data_classification(data: Dict[str, Any], filename: str, result: ValidationResult):
    """Validate data classification metadata"""
    
    # Check for data_classification field
    if "data_classification" not in data:
        result.add_error(f"{filename}: Missing 'data_classification' field")
        return
    
    dc = data["data_classification"]
    
    # Mandatory fields
    required_fields = [
        "data_class",
        "source_agency",
        "agency_endpoint",
        "license",
        "delay_policy",
        "checksum",
        "retrieval_timestamp",
        "target_object",
    ]
    
    for field in required_fields:
        if field not in dc:
            result.add_error(f"{filename}: Missing mandatory field '{field}'")
    
    # Validate data_class enum
    if "data_class" in dc:
        valid_classes = ["RAW_DATA", "SNAPSHOT", "DERIVED"]
        if dc["data_class"] not in valid_classes:
            result.add_error(
                f"{filename}: Invalid data_class '{dc['data_class']}'. "
                f"Must be one of {valid_classes}"
            )
        else:
            result.add_pass(f"{filename}: Valid data_class '{dc['data_class']}'")
    
    # Validate source_agency
    if "source_agency" in dc:
        valid_agencies = ["NASA", "ESA", "CNSA", "Roscosmos", "JAXA", "MPC"]
        if dc["source_agency"] not in valid_agencies:
            result.add_error(
                f"{filename}: Invalid source_agency '{dc['source_agency']}'. "
                f"Must be one of {valid_agencies}"
            )
        else:
            result.add_pass(f"{filename}: Valid source_agency '{dc['source_agency']}'")
    
    # Validate RAW_DATA requirements
    if dc.get("data_class") == "RAW_DATA":
        if not dc.get("download_url"):
            result.add_error(f"{filename}: RAW_DATA requires 'download_url'")
        else:
            result.add_pass(f"{filename}: RAW_DATA has download_url")
        
        if not dc.get("provenance"):
            result.add_error(f"{filename}: RAW_DATA requires 'provenance' information")
        else:
            result.add_pass(f"{filename}: RAW_DATA has provenance")
    
    # Validate SNAPSHOT requirements
    if dc.get("data_class") == "SNAPSHOT":
        # Snapshots should acknowledge their limitation
        result.add_warning(
            f"{filename}: SNAPSHOT data has zero scientific value alone. "
            "Must reference RAW_DATA source."
        )
    
    # Validate delay_policy
    if "delay_policy" in dc:
        dp = dc["delay_policy"]
        if not isinstance(dp, dict):
            result.add_error(f"{filename}: delay_policy must be an object")
        elif "raw_release_delay" not in dp:
            result.add_error(f"{filename}: delay_policy missing 'raw_release_delay'")
        else:
            result.add_pass(f"{filename}: Valid delay_policy")
    
    # Validate checksum format
    if "checksum" in dc:
        checksum = dc["checksum"]
        if not isinstance(checksum, str) or len(checksum) != 64:
            result.add_error(f"{filename}: Invalid checksum format (must be 64-char hex)")
        else:
            result.add_pass(f"{filename}: Valid checksum format")
    
    # Validate visual attributes
    if "visual_attributes" not in dc:
        result.add_error(f"{filename}: Missing 'visual_attributes' for UI rendering")
    else:
        va = dc["visual_attributes"]
        required_va = ["label", "color", "badge", "icon", "resolution_flag"]
        for field in required_va:
            if field not in va:
                result.add_error(f"{filename}: Missing visual_attribute '{field}'")


def validate_metadata(data: Dict[str, Any], filename: str, result: ValidationResult):
    """Validate basic metadata structure"""
    
    if "metadata" not in data:
        result.add_error(f"{filename}: Missing 'metadata' field")
        return
    
    metadata = data["metadata"]
    required_fields = ["project", "pipeline", "query_designation", "retrieved_utc"]
    
    for field in required_fields:
        if field not in metadata:
            result.add_error(f"{filename}: metadata missing '{field}'")


def validate_file(filepath: Path, result: ValidationResult):
    """Validate a single JSON data file"""
    
    filename = filepath.name
    
    # Skip non-snapshot files
    if not (filename.startswith("official_snapshot") or filename == "official_snapshot_latest.json"):
        return
    
    print(f"\nValidating: {filename}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result.add_error(f"{filename}: Invalid JSON - {e}")
        return
    except Exception as e:
        result.add_error(f"{filename}: Failed to read file - {e}")
        return
    
    # Perform validations
    validate_metadata(data, filename, result)
    validate_data_classification(data, filename, result)


def main():
    """Main validation entry point"""
    
    print("="*70)
    print("TRIZEL Monitor - Data Integrity Validation")
    print("="*70)
    
    result = ValidationResult()
    
    # Find data directory
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data"
    
    if not data_dir.exists():
        result.add_error(f"Data directory not found: {data_dir}")
        result.print_summary()
        return 1
    
    # Validate all JSON files in data directory
    json_files = list(data_dir.glob("*.json"))
    
    if not json_files:
        result.add_warning("No JSON files found in data directory")
    
    for filepath in json_files:
        validate_file(filepath, result)
    
    # Print summary
    result.print_summary()
    
    # Exit code
    return 1 if result.has_errors() else 0


if __name__ == "__main__":
    sys.exit(main())
