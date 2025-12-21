#!/usr/bin/env python3
"""
Validate raw record JSON against the schema and sources registry.
"""
import argparse
import json
import os
import sys
from pathlib import Path


def load_json(path: str):
    """Load and parse a JSON file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def validate_against_schema(record: dict, schema: dict) -> list:
    """Basic schema validation (subset of JSON Schema)."""
    errors = []
    
    # Check required fields
    if 'required' in schema:
        for field in schema['required']:
            if field not in record:
                errors.append(f"Missing required field: {field}")
    
    # Check properties
    if 'properties' in schema:
        for prop, prop_schema in schema['properties'].items():
            if prop in record:
                # Check type
                if 'type' in prop_schema:
                    expected_type = prop_schema['type']
                    actual_value = record[prop]
                    
                    type_map = {
                        'string': str,
                        'integer': int,
                        'object': dict,
                        'array': list,
                        'boolean': bool,
                        'number': (int, float)
                    }
                    
                    if expected_type in type_map:
                        if not isinstance(actual_value, type_map[expected_type]):
                            errors.append(f"Field '{prop}' has wrong type. Expected {expected_type}, got {type(actual_value).__name__}")
                
                # Recursively validate nested objects
                if 'type' in prop_schema and prop_schema['type'] == 'object' and 'properties' in prop_schema:
                    nested_errors = validate_against_schema(record[prop], prop_schema)
                    errors.extend([f"{prop}.{err}" for err in nested_errors])
                
                # Check const values
                if 'const' in prop_schema:
                    if record[prop] != prop_schema['const']:
                        errors.append(f"Field '{prop}' must be '{prop_schema['const']}', got '{record[prop]}'")
                
                # Check pattern for strings
                if 'pattern' in prop_schema and isinstance(record[prop], str):
                    import re
                    if not re.match(prop_schema['pattern'], record[prop]):
                        errors.append(f"Field '{prop}' does not match pattern: {prop_schema['pattern']}")
    
    return errors


def validate_against_sources(record: dict, sources: dict) -> list:
    """Validate that source references are correct."""
    errors = []
    
    if 'source' not in record:
        return errors
    
    source = record['source']
    source_id = source.get('source_id')
    endpoint_id = source.get('endpoint_id')
    
    # Check if source_id exists in registry
    if source_id and source_id not in sources.get('sources', {}):
        errors.append(f"source_id '{source_id}' not found in sources registry")
        return errors
    
    # Check if endpoint_id exists for this source
    if source_id and endpoint_id:
        source_def = sources['sources'][source_id]
        endpoints = source_def.get('endpoints', {})
        if endpoint_id not in endpoints:
            errors.append(f"endpoint_id '{endpoint_id}' not found for source '{source_id}'")
        else:
            # Validate endpoint URL matches
            expected_url = endpoints[endpoint_id].get('url')
            actual_url = source.get('endpoint_url')
            if expected_url and actual_url and expected_url != actual_url:
                errors.append(f"endpoint_url mismatch. Expected '{expected_url}', got '{actual_url}'")
    
    return errors


def validate_raw_data_file(record: dict, record_path: str) -> list:
    """Validate that the referenced raw data file exists and hash matches."""
    errors = []
    
    if 'raw_data_ref' not in record:
        return errors
    
    raw_ref = record['raw_data_ref']
    rel_path = raw_ref.get('relative_path')
    
    if not rel_path:
        return errors
    
    # Resolve relative to repository root
    record_file = Path(record_path)
    repo_root = record_file.parent
    while repo_root.parent != repo_root:
        if (repo_root / '.git').exists():
            break
        repo_root = repo_root.parent
    
    raw_file = repo_root / rel_path
    
    if not raw_file.exists():
        errors.append(f"Raw data file not found: {rel_path}")
        return errors
    
    # Verify SHA-256 hash
    if 'integrity' in record and 'sha256' in record['integrity']:
        import hashlib
        expected_hash = record['integrity']['sha256']
        
        sha256 = hashlib.sha256()
        with open(raw_file, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        actual_hash = sha256.hexdigest()
        
        if actual_hash != expected_hash:
            errors.append(f"SHA-256 hash mismatch. Expected {expected_hash}, got {actual_hash}")
        
        # Verify file size
        if 'size_bytes' in record['integrity']:
            expected_size = record['integrity']['size_bytes']
            actual_size = raw_file.stat().st_size
            if actual_size != expected_size:
                errors.append(f"File size mismatch. Expected {expected_size} bytes, got {actual_size} bytes")
    
    return errors


def main():
    parser = argparse.ArgumentParser(description='Validate raw record JSON files')
    parser.add_argument('record_path', help='Path to the raw record JSON file to validate')
    parser.add_argument('--schema', default='spec/raw_record.schema.json', help='Path to schema file')
    parser.add_argument('--sources', default='data/metadata/sources.json', help='Path to sources registry')
    
    args = parser.parse_args()
    
    # Find repository root
    current = Path(args.record_path).absolute()
    repo_root = current.parent
    while repo_root.parent != repo_root:
        if (repo_root / '.git').exists():
            break
        repo_root = repo_root.parent
    
    # Resolve schema and sources paths relative to repo root
    schema_path = repo_root / args.schema
    sources_path = repo_root / args.sources
    
    print(f"Validating: {args.record_path}")
    print(f"Schema: {schema_path}")
    print(f"Sources: {sources_path}")
    print()
    
    # Load files
    record = load_json(args.record_path)
    schema = load_json(str(schema_path))
    sources = load_json(str(sources_path))
    
    # Run validations
    all_errors = []
    
    print("1. Validating against schema...")
    schema_errors = validate_against_schema(record, schema)
    all_errors.extend(schema_errors)
    if schema_errors:
        for err in schema_errors:
            print(f"  ✗ {err}")
    else:
        print("  ✓ Schema validation passed")
    
    print()
    print("2. Validating against sources registry...")
    source_errors = validate_against_sources(record, sources)
    all_errors.extend(source_errors)
    if source_errors:
        for err in source_errors:
            print(f"  ✗ {err}")
    else:
        print("  ✓ Sources validation passed")
    
    print()
    print("3. Validating raw data file...")
    file_errors = validate_raw_data_file(record, args.record_path)
    all_errors.extend(file_errors)
    if file_errors:
        for err in file_errors:
            print(f"  ✗ {err}")
    else:
        print("  ✓ Raw data file validation passed")
    
    print()
    if all_errors:
        print(f"VALIDATION FAILED: {len(all_errors)} error(s) found")
        sys.exit(1)
    else:
        print("✓ ALL VALIDATIONS PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
