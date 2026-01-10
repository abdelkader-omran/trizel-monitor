#!/usr/bin/env python3
"""
TRIZEL Data Governance Validator

This script validates all data files against the authoritative data contract.
It enforces:
- Single metadata block (trizel_metadata only)
- No duplicated metadata blocks
- RAW_DATA classification rules
- Agency whitelist (NASA, ESA, JAXA, MPC only)
- Checksum policy (SHA-256 required, MD5 forbidden)
- Visual attributes presence and correctness
- Required fields and types

See DATA_CONTRACT.md and ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md

Exit codes:
  0 = all files valid
  1 = validation failures found
"""

import os
import sys
import json
import hashlib
from typing import Any, Dict, List, Tuple
from pathlib import Path


# Allowed values (from data contract)
ALLOWED_CLASSIFICATIONS = {"RAW_DATA", "SNAPSHOT", "DERIVED"}
ALLOWED_AGENCIES = {"NASA", "ESA", "JAXA", "MPC"}
ALLOWED_SOURCE_TYPES = {"api", "archive", "download"}
FORBIDDEN_CHECKSUMS = {"md5", "MD5"}

# Visual attributes validation
VISUAL_ATTRIBUTES_MAP = {
    "RAW_DATA": {
        "color": "green",
        "icon": "✓",
        "label": "RAW DATA"
    },
    "SNAPSHOT": {
        "color": "orange",
        "icon": "⚠",
        "label": "SNAPSHOT – NO SCIENTIFIC VALUE ALONE"
    },
    "DERIVED": {
        "color": "blue",
        "icon": "→",
        "label": "DERIVED DATA"
    }
}


class ValidationError:
    """Represents a validation error."""
    
    def __init__(self, file_path: str, rule: str, message: str, severity: str = "ERROR"):
        self.file_path = file_path
        self.rule = rule
        self.message = message
        self.severity = severity
    
    def __str__(self) -> str:
        return f"[{self.severity}] {self.file_path}: {self.rule} - {self.message}"


def find_data_files(data_dir: str) -> List[str]:
    """Find all JSON files in data directory."""
    data_path = Path(data_dir)
    if not data_path.exists():
        return []
    
    return [str(f) for f in data_path.glob("*.json")]


def load_json_file(file_path: str) -> Tuple[Dict[str, Any], List[ValidationError]]:
    """Load and parse JSON file, return data and any parse errors."""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, errors
    except json.JSONDecodeError as e:
        errors.append(ValidationError(
            file_path, "JSON_PARSE", f"Invalid JSON: {e}"
        ))
        return {}, errors
    except Exception as e:
        errors.append(ValidationError(
            file_path, "FILE_READ", f"Cannot read file: {e}"
        ))
        return {}, errors


def check_single_metadata_block(file_path: str, data: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate that exactly ONE metadata block exists at root level.
    
    RULE: trizel_metadata MUST appear ONCE and ONLY ONCE at root level.
    RULE: NO legacy keys (metadata, platforms_registry, sbdb_data, sbdb_error).
    """
    errors = []
    
    # Check for trizel_metadata presence
    if "trizel_metadata" not in data:
        errors.append(ValidationError(
            file_path, "SINGLE_METADATA_BLOCK",
            "Missing required 'trizel_metadata' block at root level"
        ))
    
    # Check for legacy/forbidden keys at root level
    forbidden_keys = {"metadata", "platforms_registry", "sbdb_data", "sbdb_error"}
    found_forbidden = forbidden_keys.intersection(data.keys())
    if found_forbidden:
        errors.append(ValidationError(
            file_path, "SINGLE_METADATA_BLOCK",
            f"Forbidden root-level keys found (legacy format): {found_forbidden}. Use 'trizel_metadata' only."
        ))
    
    # Check for duplicated metadata blocks (nested)
    def check_nested_metadata(obj: Any, path: str = "root") -> None:
        if isinstance(obj, dict):
            if path != "root" and "trizel_metadata" in obj:
                errors.append(ValidationError(
                    file_path, "NO_DUPLICATED_METADATA",
                    f"Duplicated 'trizel_metadata' block found at: {path}"
                ))
            for key, value in obj.items():
                check_nested_metadata(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_nested_metadata(item, f"{path}[{i}]")
    
    if "trizel_metadata" in data:
        check_nested_metadata(data["trizel_metadata"], "trizel_metadata")
    
    return errors


def check_required_fields(file_path: str, metadata: Dict[str, Any]) -> List[ValidationError]:
    """Validate that all required metadata fields are present."""
    errors = []
    
    required_fields = {
        "project": str,
        "pipeline": str,
        "version": str,
        "data_classification": str,
        "source_agency": str,
        "query_designation": str,
        "retrieved_utc": str,
        "checksum": dict,
        "provenance": dict,
        "visual_attributes": dict,
        "integrity": dict
    }
    
    for field, expected_type in required_fields.items():
        if field not in metadata:
            errors.append(ValidationError(
                file_path, "REQUIRED_FIELDS",
                f"Missing required field: trizel_metadata.{field}"
            ))
        elif not isinstance(metadata[field], expected_type):
            errors.append(ValidationError(
                file_path, "REQUIRED_FIELDS",
                f"Field trizel_metadata.{field} has wrong type: expected {expected_type.__name__}, got {type(metadata[field]).__name__}"
            ))
    
    # Check nested required fields
    if "checksum" in metadata and isinstance(metadata["checksum"], dict):
        if "algorithm" not in metadata["checksum"]:
            errors.append(ValidationError(
                file_path, "CHECKSUM_POLICY",
                "Missing checksum.algorithm field"
            ))
        if "value" not in metadata["checksum"]:
            errors.append(ValidationError(
                file_path, "CHECKSUM_POLICY",
                "Missing checksum.value field (SHA-256 required)"
            ))
    
    return errors


def check_data_classification(file_path: str, metadata: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate data classification rules.
    
    RULE: RAW_DATA only for direct archival downloads from official agencies.
    RULE: API responses (like JPL SBDB) MUST be SNAPSHOT.
    """
    errors = []
    
    classification = metadata.get("data_classification")
    agency = metadata.get("source_agency")
    source_type = metadata.get("provenance", {}).get("source_type")
    source_url = metadata.get("provenance", {}).get("source_url", "")
    
    # Check classification is allowed
    if classification not in ALLOWED_CLASSIFICATIONS:
        errors.append(ValidationError(
            file_path, "DATA_CLASSIFICATION",
            f"Invalid classification '{classification}'. Must be one of: {ALLOWED_CLASSIFICATIONS}"
        ))
        return errors
    
    # RAW_DATA rules (STRICT)
    if classification == "RAW_DATA":
        # RAW_DATA requires direct download (not API)
        if source_type == "api":
            errors.append(ValidationError(
                file_path, "RAW_DATA_RULES",
                "RAW_DATA classification not allowed for API sources (source_type='api'). API responses must be classified as SNAPSHOT. For RAW_DATA, use source_type='archive' or 'download'."
            ))
        
        # RAW_DATA requires official agency
        if agency not in ALLOWED_AGENCIES:
            errors.append(ValidationError(
                file_path, "RAW_DATA_RULES",
                f"RAW_DATA classification requires official agency. Got '{agency}', expected one of: {ALLOWED_AGENCIES}"
            ))
    
    # SNAPSHOT rules
    if classification == "SNAPSHOT" and source_type != "api":
        # This is a warning, not an error - SNAPSHOT can be used for non-API sources
        errors.append(ValidationError(
            file_path, "DATA_CLASSIFICATION",
            f"SNAPSHOT classification typically used for API sources, but source_type is '{source_type}'",
            severity="WARNING"
        ))
    
    # Special check: JPL SBDB API must be SNAPSHOT
    if "jpl.nasa.gov" in source_url.lower() and "sbdb" in source_url.lower():
        if classification != "SNAPSHOT":
            errors.append(ValidationError(
                file_path, "RAW_DATA_RULES",
                f"JPL SBDB API responses MUST be classified as SNAPSHOT (computed values), not {classification}"
            ))
    
    return errors


def check_agency_whitelist(file_path: str, metadata: Dict[str, Any]) -> List[ValidationError]:
    """Validate that only allowed agencies are used."""
    errors = []
    
    agency = metadata.get("source_agency")
    if agency and agency not in ALLOWED_AGENCIES:
        errors.append(ValidationError(
            file_path, "AGENCY_WHITELIST",
            f"Invalid agency '{agency}'. Only allowed: {ALLOWED_AGENCIES}"
        ))
    
    return errors


def check_checksum_policy(file_path: str, metadata: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate checksum policy.
    
    RULE: SHA-256 required.
    RULE: MD5 absolutely forbidden.
    """
    errors = []
    
    checksum = metadata.get("checksum", {})
    
    # Check for forbidden MD5
    if "md5" in checksum or "MD5" in checksum:
        errors.append(ValidationError(
            file_path, "CHECKSUM_POLICY",
            "MD5 checksums are FORBIDDEN (cryptographically broken). Use SHA-256 only."
        ))
    
    # Check algorithm field
    algorithm = checksum.get("algorithm", "").lower()
    if algorithm not in {"sha256", "sha-256"}:
        errors.append(ValidationError(
            file_path, "CHECKSUM_POLICY",
            f"Invalid checksum algorithm '{algorithm}'. Must be 'sha256'."
        ))
    
    # Check SHA-256 value presence
    if "value" not in checksum or not checksum["value"]:
        errors.append(ValidationError(
            file_path, "CHECKSUM_POLICY",
            "Missing SHA-256 checksum value (required)"
        ))
    
    # Validate SHA-256 format (64 lowercase hex characters)
    sha256_value = checksum.get("value", "")
    if sha256_value:
        if len(sha256_value) != 64:
            errors.append(ValidationError(
                file_path, "CHECKSUM_POLICY",
                f"Invalid SHA-256 length (must be 64 characters): got {len(sha256_value)}"
            ))
        elif not all(c in "0123456789abcdef" for c in sha256_value):
            errors.append(ValidationError(
                file_path, "CHECKSUM_POLICY",
                f"Invalid SHA-256 format (must be lowercase hex): {sha256_value[:20]}..."
            ))
    
    return errors


def check_visual_attributes(file_path: str, metadata: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate visual attributes presence and correctness.
    
    RULE: Visual attributes must match data classification.
    """
    errors = []
    
    classification = metadata.get("data_classification")
    visual = metadata.get("visual_attributes", {})
    
    if not visual:
        errors.append(ValidationError(
            file_path, "VISUAL_ATTRIBUTES",
            "Missing visual_attributes block (required)"
        ))
        return errors
    
    # Check required fields
    required_visual_fields = {"color", "icon", "label"}
    missing_fields = required_visual_fields - visual.keys()
    if missing_fields:
        errors.append(ValidationError(
            file_path, "VISUAL_ATTRIBUTES",
            f"Missing visual_attributes fields: {missing_fields}"
        ))
    
    # Check values match classification
    if classification in VISUAL_ATTRIBUTES_MAP:
        expected = VISUAL_ATTRIBUTES_MAP[classification]
        for key, expected_value in expected.items():
            actual_value = visual.get(key)
            if actual_value != expected_value:
                errors.append(ValidationError(
                    file_path, "VISUAL_ATTRIBUTES",
                    f"Visual attribute '{key}' mismatch for {classification}: expected '{expected_value}', got '{actual_value}'"
                ))
    
    return errors


def check_md5_in_file(file_path: str) -> List[ValidationError]:
    """
    Check for MD5 usage in data files (forbidden).
    
    RULE: MD5 checksums are forbidden in data files (cryptographically broken).
    Note: This only checks for MD5 in the actual checksum fields, not in documentation.
    """
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if there's an MD5 checksum in the metadata
        if "trizel_metadata" in data:
            checksum = data["trizel_metadata"].get("checksum", {})
            # Check for MD5 in algorithm field or as a checksum key
            if checksum.get("algorithm", "").lower() == "md5":
                errors.append(ValidationError(
                    file_path, "CHECKSUM_POLICY",
                    "MD5 algorithm found in checksum (FORBIDDEN - cryptographically broken). Use SHA-256 only."
                ))
            if "md5" in checksum or "MD5" in checksum:
                errors.append(ValidationError(
                    file_path, "CHECKSUM_POLICY",
                    "MD5 checksum field found (FORBIDDEN - cryptographically broken). Use SHA-256 only."
                ))
    except (json.JSONDecodeError, Exception):
        pass  # Not a valid JSON file or already caught by other validators
    
    return errors


def validate_file(file_path: str) -> List[ValidationError]:
    """Validate a single data file against all rules."""
    all_errors = []
    
    # Skip non-JSON files
    if not file_path.endswith('.json'):
        return all_errors
    
    # Load file
    data, load_errors = load_json_file(file_path)
    all_errors.extend(load_errors)
    if load_errors:
        return all_errors  # Can't validate further if JSON is invalid
    
    # Check for MD5 in file content
    all_errors.extend(check_md5_in_file(file_path))
    
    # Check single metadata block
    all_errors.extend(check_single_metadata_block(file_path, data))
    
    # If no trizel_metadata, can't validate further
    if "trizel_metadata" not in data:
        return all_errors
    
    metadata = data["trizel_metadata"]
    
    # Run all validation checks
    all_errors.extend(check_required_fields(file_path, metadata))
    all_errors.extend(check_data_classification(file_path, metadata))
    all_errors.extend(check_agency_whitelist(file_path, metadata))
    all_errors.extend(check_checksum_policy(file_path, metadata))
    all_errors.extend(check_visual_attributes(file_path, metadata))
    
    return all_errors


def main():
    """Main validation entry point."""
    data_dir = os.getenv("DATA_DIR", "data")
    
    print("=" * 80)
    print("TRIZEL Data Governance Validator")
    print("=" * 80)
    print(f"Data directory: {data_dir}")
    print()
    
    # Find all data files
    data_files = find_data_files(data_dir)
    if not data_files:
        print(f"No JSON files found in {data_dir}")
        return 0
    
    print(f"Found {len(data_files)} JSON files to validate")
    print()
    
    # Validate each file
    all_errors = []
    file_status = {}
    
    for file_path in sorted(data_files):
        errors = validate_file(file_path)
        all_errors.extend(errors)
        
        error_count = sum(1 for e in errors if e.severity == "ERROR")
        warning_count = sum(1 for e in errors if e.severity == "WARNING")
        
        file_status[file_path] = {
            "errors": error_count,
            "warnings": warning_count,
            "status": "PASS" if error_count == 0 else "FAIL"
        }
    
    # Print results
    print("-" * 80)
    print("Validation Results:")
    print("-" * 80)
    
    for file_path in sorted(file_status.keys()):
        status = file_status[file_path]
        symbol = "✓" if status["status"] == "PASS" else "✗"
        print(f"{symbol} {file_path}: {status['status']} "
              f"({status['errors']} errors, {status['warnings']} warnings)")
    
    print()
    
    # Print all errors
    if all_errors:
        print("-" * 80)
        print("Validation Errors:")
        print("-" * 80)
        for error in all_errors:
            print(error)
        print()
    
    # Summary
    total_errors = sum(1 for e in all_errors if e.severity == "ERROR")
    total_warnings = sum(1 for e in all_errors if e.severity == "WARNING")
    passed_files = sum(1 for s in file_status.values() if s["status"] == "PASS")
    failed_files = len(file_status) - passed_files
    
    print("=" * 80)
    print(f"Summary: {passed_files} passed, {failed_files} failed")
    print(f"Total: {total_errors} errors, {total_warnings} warnings")
    print("=" * 80)
    
    # Exit code
    if total_errors > 0:
        print("\nValidation FAILED")
        return 1
    else:
        print("\nValidation PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
