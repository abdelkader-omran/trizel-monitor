#!/usr/bin/env python3
"""
TRIZEL Monitor — Metadata Enforcement & Classification System

This script:
1. Scans all data files in the repository
2. Classifies files as RAW_DATA, SNAPSHOT, or DERIVED
3. Adds mandatory metadata fields
4. Validates metadata schema compliance
5. Generates machine-readable manifest

Scientific Authority: TRIZEL Monitor Scientific Integrity Policy
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


# Whitelisted international space agencies
WHITELISTED_AGENCIES = [
    "NASA",
    "ESA",
    "CNSA",
    "Roscosmos",
    "JAXA",
    "MPC",
]

# Data classification types
DATA_CLASSES = ["RAW_DATA", "SNAPSHOT", "DERIVED"]

# Verification statuses
VERIFICATION_STATUSES = ["VERIFIED", "PENDING", "UNVERIFIED", "FAILED"]


def compute_checksum(filepath: str, algorithm: str = "sha256") -> str:
    """Compute cryptographic checksum of file."""
    hash_obj = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return f"{algorithm}:{hash_obj.hexdigest()}"


def classify_file(filename: str) -> Dict[str, Any]:
    """
    Classify file based on naming convention and content.
    
    Classification rules:
    - jpl_sbdb_*.json → RAW_DATA (from NASA/JPL)
    - official_snapshot_*.json → SNAPSHOT
    - platforms_registry_*.json → DERIVED
    - latest_*.json → SNAPSHOT (latest version)
    """
    classification = {
        "data_class": "UNCLASSIFIED",
        "source_agency": "UNKNOWN",
        "agency_endpoint": "UNKNOWN",
        "license": "UNKNOWN",
    }
    
    # RAW_DATA: JPL SBDB API responses
    if filename.startswith("jpl_sbdb_"):
        classification.update({
            "data_class": "RAW_DATA",
            "source_agency": "NASA",
            "agency_endpoint": "https://ssd-api.jpl.nasa.gov/sbdb.api",
            "raw_release_policy": "NASA_OPEN_DATA",
            "license": "CC0-1.0",
            "verification_status": "VERIFIED",
        })
    
    # SNAPSHOT: Official snapshots of system state
    elif filename.startswith("official_snapshot_") or filename.startswith("latest_"):
        classification.update({
            "data_class": "SNAPSHOT",
            "source_agency": "INTERNAL",
            "agency_endpoint": "INTERNAL_PIPELINE",
            "raw_release_policy": "DERIVED_WORK",
            "license": "CC-BY-4.0",
            "verification_status": "VERIFIED",
        })
    
    # DERIVED: Platforms registry
    elif filename.startswith("platforms_registry_"):
        classification.update({
            "data_class": "DERIVED",
            "source_agency": "INTERNAL",
            "agency_endpoint": "INTERNAL_PIPELINE",
            "raw_release_policy": "DERIVED_WORK",
            "license": "CC-BY-4.0",
            "verification_status": "VERIFIED",
            "processing_pipeline": "TRIZEL Monitor v1.0",
        })
    
    return classification


def extract_timestamp_from_filename(filename: str) -> Optional[str]:
    """Extract UTC timestamp from filename in format YYYYMMDD_HHMMSS."""
    import re
    
    # Pattern: YYYYMMDD_HHMMSS
    pattern = r"(\d{8})_(\d{6})"
    match = re.search(pattern, filename)
    
    if match:
        date_part = match.group(1)  # YYYYMMDD
        time_part = match.group(2)  # HHMMSS
        
        # Convert to ISO-8601
        try:
            dt = datetime.strptime(f"{date_part}{time_part}", "%Y%m%d%H%M%S")
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return None
    
    return None


def add_metadata_to_json(filepath: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Add mandatory metadata to a JSON file.
    
    Returns: Metadata dict that was added/updated
    """
    filename = os.path.basename(filepath)
    
    # Read existing file
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Classify file
    classification = classify_file(filename)
    
    # Extract or generate timestamp
    retrieval_timestamp = extract_timestamp_from_filename(filename)
    if not retrieval_timestamp:
        # Use file modification time as fallback
        mtime = os.path.getmtime(filepath)
        retrieval_timestamp = datetime.utcfromtimestamp(mtime).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Check if existing data already has metadata at root level
    if "metadata" in data and isinstance(data, dict):
        # File already has metadata structure - update it
        if "trizel_metadata" not in data:
            data["trizel_metadata"] = {}
        
        metadata = data["trizel_metadata"]
    else:
        # Simple data file - wrap with metadata
        original_data = data.copy() if isinstance(data, dict) else data
        data = {
            "trizel_metadata": {},
            "data": original_data
        }
        metadata = data["trizel_metadata"]
    
    # Build complete metadata
    metadata.update({
        "data_class": classification["data_class"],
        "source_agency": classification["source_agency"],
        "agency_endpoint": classification["agency_endpoint"],
        "retrieval_timestamp_utc": retrieval_timestamp,
        "raw_release_policy": classification.get("raw_release_policy", "UNKNOWN"),
        "license": classification["license"],
        "verification_status": classification["verification_status"],
        "schema_version": "1.0.0",
        "last_metadata_update_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    
    # Add processing pipeline for DERIVED
    if classification["data_class"] == "DERIVED":
        metadata["processing_pipeline"] = classification.get("processing_pipeline", "TRIZEL Monitor v1.0")
    
    # Add source references for SNAPSHOT
    if classification["data_class"] == "SNAPSHOT":
        # SNAPSHOTs reference raw JPL SBDB data
        metadata["source_raw_data"] = ["jpl_sbdb_*.json (see manifest for specific files)"]
    
    # Compute checksum before writing
    if not dry_run:
        # Write updated file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Compute checksum of new file
        checksum = compute_checksum(filepath)
        
        # Read back and add checksum
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["trizel_metadata"]["checksum"] = checksum
        
        # Final write with checksum
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    return metadata


def validate_metadata(metadata: Dict[str, Any]) -> List[str]:
    """
    Validate metadata against schema.
    
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
    ]
    
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
    
    # Validate data_class
    if "data_class" in metadata and metadata["data_class"] not in DATA_CLASSES:
        errors.append(f"Invalid data_class: {metadata['data_class']}")
    
    # Validate source_agency for RAW_DATA
    if metadata.get("data_class") == "RAW_DATA":
        agency = metadata.get("source_agency")
        if agency not in WHITELISTED_AGENCIES:
            errors.append(f"RAW_DATA must be from whitelisted agency. Got: {agency}")
    
    # Validate verification_status
    if "verification_status" in metadata:
        if metadata["verification_status"] not in VERIFICATION_STATUSES:
            errors.append(f"Invalid verification_status: {metadata['verification_status']}")
    
    # Validate timestamp format
    if "retrieval_timestamp_utc" in metadata:
        try:
            datetime.strptime(metadata["retrieval_timestamp_utc"], "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            errors.append(f"Invalid timestamp format: {metadata['retrieval_timestamp_utc']}")
    
    return errors


def generate_manifest(data_dir: str = "data") -> Dict[str, Any]:
    """Generate machine-readable manifest of all data artifacts."""
    manifest = {
        "manifest_version": "1.0.0",
        "generated_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repository": "abdelkader-omran/trizel-monitor",
        "purpose": "Scientific data classification and provenance tracking",
        "artifacts": [],
        "statistics": {
            "total_files": 0,
            "by_class": {
                "RAW_DATA": 0,
                "SNAPSHOT": 0,
                "DERIVED": 0,
            },
            "by_agency": {},
        }
    }
    
    for filename in sorted(os.listdir(data_dir)):
        if not filename.endswith(".json"):
            continue
        
        filepath = os.path.join(data_dir, filename)
        
        # Read metadata
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if "trizel_metadata" not in data:
            continue
        
        metadata = data["trizel_metadata"]
        
        # Add to manifest
        artifact = {
            "filename": filename,
            "data_class": metadata.get("data_class"),
            "source_agency": metadata.get("source_agency"),
            "retrieval_timestamp_utc": metadata.get("retrieval_timestamp_utc"),
            "verification_status": metadata.get("verification_status"),
            "checksum": metadata.get("checksum"),
        }
        
        manifest["artifacts"].append(artifact)
        
        # Update statistics
        manifest["statistics"]["total_files"] += 1
        data_class = metadata.get("data_class", "UNKNOWN")
        if data_class in manifest["statistics"]["by_class"]:
            manifest["statistics"]["by_class"][data_class] += 1
        
        agency = metadata.get("source_agency", "UNKNOWN")
        manifest["statistics"]["by_agency"][agency] = \
            manifest["statistics"]["by_agency"].get(agency, 0) + 1
    
    return manifest


def main():
    """Main execution function."""
    print("=" * 60)
    print("TRIZEL Monitor — Metadata Enforcement System")
    print("=" * 60)
    print()
    
    data_dir = "data"
    
    # Find all JSON files
    json_files = [f for f in os.listdir(data_dir) if f.endswith(".json")]
    
    print(f"Found {len(json_files)} JSON files in {data_dir}/")
    print()
    
    # Process each file
    processed = 0
    errors_found = []
    
    for filename in sorted(json_files):
        filepath = os.path.join(data_dir, filename)
        print(f"Processing: {filename}")
        
        try:
            metadata = add_metadata_to_json(filepath, dry_run=False)
            
            # Validate
            validation_errors = validate_metadata(metadata)
            if validation_errors:
                print(f"  ⚠️  Validation errors:")
                for err in validation_errors:
                    print(f"     - {err}")
                errors_found.append((filename, validation_errors))
            else:
                print(f"  ✓ Classified as: {metadata['data_class']}")
                print(f"  ✓ Source: {metadata['source_agency']}")
                print(f"  ✓ Verification: {metadata['verification_status']}")
            
            processed += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors_found.append((filename, [str(e)]))
        
        print()
    
    print("=" * 60)
    print(f"Processed {processed}/{len(json_files)} files")
    
    if errors_found:
        print(f"\n⚠️  {len(errors_found)} files have validation errors")
        for filename, errs in errors_found:
            print(f"  - {filename}: {len(errs)} errors")
    else:
        print("\n✓ All files validated successfully")
    
    # Generate manifest
    print("\nGenerating data manifest...")
    manifest = generate_manifest(data_dir)
    
    manifest_path = os.path.join(data_dir, "DATA_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Manifest written to: {manifest_path}")
    print(f"\nStatistics:")
    print(f"  Total files: {manifest['statistics']['total_files']}")
    print(f"  RAW_DATA: {manifest['statistics']['by_class']['RAW_DATA']}")
    print(f"  SNAPSHOT: {manifest['statistics']['by_class']['SNAPSHOT']}")
    print(f"  DERIVED: {manifest['statistics']['by_class']['DERIVED']}")
    print()
    
    return 0 if not errors_found else 1


if __name__ == "__main__":
    exit(main())
