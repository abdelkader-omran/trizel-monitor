#!/usr/bin/env python3
"""
TRIZEL Monitor - Complete System Validator

This script validates the entire TRIZEL Monitor system including:
- Agency registry completeness
- Required agencies presence (NASA, ESA, JAXA, CNSA, ROSCOSMOS, MPC)
- Data contract compliance
- Visual differentiation
- Documentation presence

Exit codes:
  0 = all validation passed
  1 = validation failures found
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any


class SystemValidationError:
    """Represents a system-level validation error."""
    
    def __init__(self, component: str, rule: str, message: str, severity: str = "ERROR"):
        self.component = component
        self.rule = rule
        self.message = message
        self.severity = severity
    
    def __str__(self) -> str:
        return f"[{self.severity}] {self.component}: {self.rule} - {self.message}"


def validate_agency_registry() -> List[SystemValidationError]:
    """Validate the agency registry structure and completeness."""
    errors = []
    
    repo_root = Path(__file__).parent.parent
    registry_path = repo_root / "config" / "agency_registry.json"
    
    # Check file exists
    if not registry_path.exists():
        errors.append(SystemValidationError(
            "agency_registry", "FILE_EXISTS",
            f"Agency registry not found at {registry_path}"
        ))
        return errors
    
    # Load and validate structure
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(SystemValidationError(
            "agency_registry", "JSON_VALID",
            f"Invalid JSON in agency registry: {e}"
        ))
        return errors
    
    # Check required top-level fields
    if "agencies" not in registry:
        errors.append(SystemValidationError(
            "agency_registry", "REQUIRED_FIELDS",
            "Missing 'agencies' field in registry"
        ))
        return errors
    
    agencies = registry["agencies"]
    
    # Check required agencies
    required_agencies = {"NASA", "ESA", "JAXA", "CNSA", "ROSCOSMOS", "MPC"}
    present_agencies = {a.get("agency_id") for a in agencies}
    
    missing_agencies = required_agencies - present_agencies
    if missing_agencies:
        errors.append(SystemValidationError(
            "agency_registry", "REQUIRED_AGENCIES",
            f"Missing required agencies: {missing_agencies}"
        ))
    
    # Validate each agency structure
    for agency in agencies:
        agency_id = agency.get("agency_id", "UNKNOWN")
        
        # Check required fields
        required_fields = ["agency_id", "name", "status", "endpoints"]
        for field in required_fields:
            if field not in agency:
                errors.append(SystemValidationError(
                    "agency_registry", f"AGENCY_{agency_id}",
                    f"Missing required field '{field}' for {agency_id}"
                ))
        
        # Validate endpoints
        endpoints = agency.get("endpoints", [])
        for i, endpoint in enumerate(endpoints):
            endpoint_id = endpoint.get("endpoint_id", f"endpoint_{i}")
            
            required_endpoint_fields = [
                "endpoint_id", "url", "data_type", "requires_auth",
                "license_or_policy_ref", "delay_policy_default",
                "download_mode", "verification_method"
            ]
            
            for field in required_endpoint_fields:
                if field not in endpoint:
                    errors.append(SystemValidationError(
                        "agency_registry", f"ENDPOINT_{agency_id}_{endpoint_id}",
                        f"Missing required field '{field}'"
                    ))
    
    return errors


def validate_documentation_structure() -> List[SystemValidationError]:
    """Validate required documentation files exist."""
    errors = []
    
    repo_root = Path(__file__).parent.parent
    
    required_docs = {
        "docs/governance/AUTHORITATIVE_RAW_DATA_GOVERNANCE.md": "Governance document",
        "docs/governance/SUPERSESSION_NOTICE.md": "Supersession notice",
        "docs/audit/AGENCY_CONNECTIVITY_AUDIT.json": "Audit report",
        "docs/status/AGENCY_CONNECTIVITY_STATUS.md": "Status document",
        "DATA_CONTRACT.md": "Data contract",
        "README.md": "README",
    }
    
    for doc_path, description in required_docs.items():
        full_path = repo_root / doc_path
        if not full_path.exists():
            errors.append(SystemValidationError(
                "documentation", "FILE_EXISTS",
                f"Missing required document: {doc_path} ({description})"
            ))
    
    return errors


def validate_download_system() -> List[SystemValidationError]:
    """Validate RAW data download system structure."""
    errors = []
    
    repo_root = Path(__file__).parent.parent
    
    # Check download module exists
    download_module = repo_root / "src" / "raw_download" / "__init__.py"
    if not download_module.exists():
        errors.append(SystemValidationError(
            "download_system", "MODULE_EXISTS",
            f"RAW data download module not found at {download_module}"
        ))
    
    # Check storage directories
    raw_data_dir = repo_root / "data" / "raw"
    if not raw_data_dir.exists():
        errors.append(SystemValidationError(
            "download_system", "STORAGE_DIR",
            f"RAW data storage directory not found at {raw_data_dir}"
        ))
    
    return errors


def validate_scripts() -> List[SystemValidationError]:
    """Validate required automation scripts exist."""
    errors = []
    
    repo_root = Path(__file__).parent.parent
    
    required_scripts = {
        "scripts/generate_audit.py": "Audit generator",
        "scripts/generate_status.py": "Status generator",
    }
    
    for script_path, description in required_scripts.items():
        full_path = repo_root / script_path
        if not full_path.exists():
            errors.append(SystemValidationError(
                "automation_scripts", "SCRIPT_EXISTS",
                f"Missing required script: {script_path} ({description})"
            ))
    
    return errors


def validate_visual_differentiation() -> List[SystemValidationError]:
    """Validate visual attribute consistency."""
    errors = []
    
    # This checks that the system has consistent visual attribute definitions
    # The actual validation of data files is done by validate_data.py
    
    expected_visual_attrs = {
        "RAW_DATA": {"color": "green", "icon": "✓", "label": "RAW DATA"},
        "SNAPSHOT": {"color": "orange", "icon": "⚠", "label": "SNAPSHOT – NO SCIENTIFIC VALUE ALONE"},
        "DERIVED": {"color": "blue", "icon": "→", "label": "DERIVED DATA"}
    }
    
    # Check that visual attributes are documented
    repo_root = Path(__file__).parent.parent
    governance_doc = repo_root / "docs" / "governance" / "AUTHORITATIVE_RAW_DATA_GOVERNANCE.md"
    
    if governance_doc.exists():
        with open(governance_doc, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for presence of visual attribute definitions
        for classification, attrs in expected_visual_attrs.items():
            if classification not in content:
                errors.append(SystemValidationError(
                    "visual_differentiation", "DOCUMENTATION",
                    f"Classification {classification} not documented in governance",
                    severity="WARNING"
                ))
    
    return errors


def main():
    """Main validation entry point."""
    print("=" * 80)
    print("TRIZEL Monitor - Complete System Validator")
    print("=" * 80)
    print()
    
    all_errors = []
    
    # Run all validation checks
    print("Validating agency registry...")
    all_errors.extend(validate_agency_registry())
    
    print("Validating documentation structure...")
    all_errors.extend(validate_documentation_structure())
    
    print("Validating download system...")
    all_errors.extend(validate_download_system())
    
    print("Validating automation scripts...")
    all_errors.extend(validate_scripts())
    
    print("Validating visual differentiation...")
    all_errors.extend(validate_visual_differentiation())
    
    print()
    print("-" * 80)
    print("Validation Results:")
    print("-" * 80)
    
    # Group errors by severity
    errors = [e for e in all_errors if e.severity == "ERROR"]
    warnings = [e for e in all_errors if e.severity == "WARNING"]
    
    # Print errors
    if errors:
        print("\nERRORS:")
        for error in errors:
            print(f"  {error}")
    
    # Print warnings
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    
    print()
    print("=" * 80)
    print(f"Summary: {len(errors)} errors, {len(warnings)} warnings")
    print("=" * 80)
    
    # Exit code
    if errors:
        print("\nSystem validation FAILED")
        return 1
    else:
        print("\nSystem validation PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
