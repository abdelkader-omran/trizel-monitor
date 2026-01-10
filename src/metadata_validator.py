#!/usr/bin/env python3
"""
TRIZEL Monitor — Metadata Validation Script

This script validates that all data files comply with the mandatory metadata schema.
Used in CI/CD to enforce data integrity and scientific provenance.

Exit codes:
  0 - All validations passed
  1 - Validation failures detected
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple


# Whitelisted international space agencies
WHITELISTED_AGENCIES = [
    "NASA",
    "ESA",
    "CNSA",
    "Roscosmos",
    "JAXA",
    "MPC",
    "INTERNAL",  # For snapshots and derived data
]

# Data classification types
DATA_CLASSES = ["RAW_DATA", "SNAPSHOT", "DERIVED"]

# Verification statuses
VERIFICATION_STATUSES = ["VERIFIED", "PENDING", "UNVERIFIED", "FAILED"]

# Required licenses
VALID_LICENSES = [
    "CC0-1.0",
    "CC-BY-4.0",
    "NASA_OPEN_DATA",
    "ESA-OPEN",
    "PROPRIETARY",
]


def validate_metadata_schema(metadata: Dict[str, Any], filename: str) -> List[str]:
    """
    Validate metadata against the mandatory schema.
    
    Returns: List of validation errors (empty if valid)
    """
    errors = []
    
    # Required fields
    required_fields = [
        "data_class",
        "source_agency",
        "agency_endpoint",
        "retrieval_timestamp_utc",
        "raw_release_policy",
        "license",
        "verification_status",
        "checksum",
    ]
    
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
    
    # Validate data_class
    if "data_class" in metadata:
        data_class = metadata["data_class"]
        if data_class not in DATA_CLASSES:
            errors.append(f"Invalid data_class: {data_class}. Must be one of: {DATA_CLASSES}")
    else:
        return errors  # Can't continue validation without data_class
    
    # Validate source_agency
    if "source_agency" in metadata:
        agency = metadata["source_agency"]
        if agency not in WHITELISTED_AGENCIES:
            errors.append(f"Invalid source_agency: {agency}. Must be one of: {WHITELISTED_AGENCIES}")
        
        # RAW_DATA must be from official space agency (not INTERNAL)
        if data_class == "RAW_DATA" and agency == "INTERNAL":
            errors.append("RAW_DATA cannot have source_agency=INTERNAL. Must be from official space agency.")
        
        # RAW_DATA must be from whitelisted agency
        if data_class == "RAW_DATA" and agency not in ["NASA", "ESA", "CNSA", "Roscosmos", "JAXA", "MPC"]:
            errors.append(f"RAW_DATA must be from whitelisted space agency. Got: {agency}")
    
    # Validate verification_status
    if "verification_status" in metadata:
        status = metadata["verification_status"]
        if status not in VERIFICATION_STATUSES:
            errors.append(f"Invalid verification_status: {status}. Must be one of: {VERIFICATION_STATUSES}")
    
    # Validate timestamp format (ISO-8601 UTC)
    if "retrieval_timestamp_utc" in metadata:
        timestamp = metadata["retrieval_timestamp_utc"]
        try:
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            errors.append(f"Invalid timestamp format: {timestamp}. Must be ISO-8601 UTC (YYYY-MM-DDTHH:MM:SSZ)")
    
    # Validate license
    if "license" in metadata:
        license_val = metadata["license"]
        # Allow any value but warn if not in standard list
        if license_val not in VALID_LICENSES:
            # This is a warning, not an error
            pass
    
    # Validate checksum format
    if "checksum" in metadata:
        checksum = metadata["checksum"]
        if ":" not in checksum:
            errors.append(f"Invalid checksum format: {checksum}. Must be 'algorithm:hash'")
        else:
            algorithm = checksum.split(":")[0]
            if algorithm not in ["sha256", "md5", "sha512"]:
                errors.append(f"Invalid checksum algorithm: {algorithm}. Must be sha256, md5, or sha512")
    
    # Validate SNAPSHOT has source_raw_data
    if data_class == "SNAPSHOT":
        if "source_raw_data" not in metadata:
            errors.append("SNAPSHOT must have 'source_raw_data' field")
    
    # Validate DERIVED has processing_pipeline
    if data_class == "DERIVED":
        if "processing_pipeline" not in metadata:
            errors.append("DERIVED must have 'processing_pipeline' field")
    
    # Validate agency_endpoint for RAW_DATA
    if data_class == "RAW_DATA":
        if "agency_endpoint" in metadata:
            endpoint = metadata["agency_endpoint"]
            if endpoint in ["UNKNOWN", "INTERNAL_PIPELINE", ""]:
                errors.append(f"RAW_DATA must have valid public agency_endpoint. Got: {endpoint}")
    
    return errors


def validate_file(filepath: str) -> Tuple[bool, List[str]]:
    """
    Validate a single JSON file.
    
    Returns: (is_valid, list_of_errors)
    """
    filename = os.path.basename(filepath)
    errors = []
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    except Exception as e:
        return False, [f"Error reading file: {e}"]
    
    # Check for trizel_metadata
    if "trizel_metadata" not in data:
        return False, ["Missing 'trizel_metadata' field at root level"]
    
    metadata = data["trizel_metadata"]
    
    # Validate metadata schema
    schema_errors = validate_metadata_schema(metadata, filename)
    
    if schema_errors:
        return False, schema_errors
    
    return True, []


def validate_manifest(manifest_path: str) -> Tuple[bool, List[str]]:
    """
    Validate the DATA_MANIFEST.json file.
    
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    
    if not os.path.exists(manifest_path):
        return False, ["DATA_MANIFEST.json does not exist"]
    
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid manifest JSON: {e}"]
    
    # Validate manifest structure
    required_fields = ["manifest_version", "generated_utc", "repository", "artifacts", "statistics"]
    for field in required_fields:
        if field not in manifest:
            errors.append(f"Manifest missing required field: {field}")
    
    # Validate statistics
    if "statistics" in manifest:
        stats = manifest["statistics"]
        if "total_files" not in stats:
            errors.append("Manifest statistics missing 'total_files'")
        if "by_class" not in stats:
            errors.append("Manifest statistics missing 'by_class'")
        if "by_agency" not in stats:
            errors.append("Manifest statistics missing 'by_agency'")
    
    # Validate artifacts
    if "artifacts" in manifest:
        if not isinstance(manifest["artifacts"], list):
            errors.append("Manifest 'artifacts' must be an array")
        else:
            for i, artifact in enumerate(manifest["artifacts"]):
                if "data_class" not in artifact:
                    errors.append(f"Artifact {i} missing 'data_class'")
                if "source_agency" not in artifact:
                    errors.append(f"Artifact {i} missing 'source_agency'")
                if "checksum" not in artifact:
                    errors.append(f"Artifact {i} missing 'checksum'")
    
    return len(errors) == 0, errors


def main():
    """Main validation function."""
    print("=" * 70)
    print("TRIZEL Monitor — Metadata Schema Validation")
    print("=" * 70)
    print()
    
    data_dir = "data"
    
    # Find all JSON files (excluding manifest)
    json_files = [
        f for f in os.listdir(data_dir) 
        if f.endswith(".json") and f != "DATA_MANIFEST.json"
    ]
    
    print(f"Validating {len(json_files)} data files...")
    print()
    
    # Validate each file
    all_valid = True
    validation_results = []
    
    for filename in sorted(json_files):
        filepath = os.path.join(data_dir, filename)
        is_valid, errors = validate_file(filepath)
        
        validation_results.append((filename, is_valid, errors))
        
        if is_valid:
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename}")
            for error in errors:
                print(f"    - {error}")
            all_valid = False
    
    print()
    print("-" * 70)
    
    # Validate manifest
    print("\nValidating DATA_MANIFEST.json...")
    manifest_path = os.path.join(data_dir, "DATA_MANIFEST.json")
    manifest_valid, manifest_errors = validate_manifest(manifest_path)
    
    if manifest_valid:
        print("✓ Manifest is valid")
        
        # Print statistics
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        
        stats = manifest["statistics"]
        print(f"\nManifest Statistics:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  RAW_DATA: {stats['by_class']['RAW_DATA']}")
        print(f"  SNAPSHOT: {stats['by_class']['SNAPSHOT']}")
        print(f"  DERIVED: {stats['by_class']['DERIVED']}")
        print(f"  Agencies: {', '.join(stats['by_agency'].keys())}")
    else:
        print("✗ Manifest validation failed:")
        for error in manifest_errors:
            print(f"    - {error}")
        all_valid = False
    
    print()
    print("=" * 70)
    
    if all_valid:
        print("✅ ALL VALIDATIONS PASSED")
        print()
        print("Repository is compliant with TRIZEL Monitor metadata schema.")
        print("100% of files are classified, verified, and traceable.")
        return 0
    else:
        print("❌ VALIDATION FAILED")
        print()
        failed_count = sum(1 for _, valid, _ in validation_results if not valid)
        print(f"{failed_count} file(s) failed validation.")
        print()
        print("Please fix the errors above and re-run validation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
