# TRIZEL Monitor Scripts

This directory contains the core scripts for the TRIZEL Monitor data acquisition and validation system.

---

## Scripts Overview

### 1. `main.py` — Data Acquisition Pipeline

**Purpose:** Automated data acquisition from NASA/JPL SBDB API

**Features:**
- Fetches orbital and physical parameters for 3I/ATLAS
- Generates timestamped snapshots with metadata
- Creates platform registry snapshots
- Automatic metadata enforcement (TRIZEL schema v1.0.0)
- Exit code contract compliance

**Usage:**
```bash
python src/main.py
```

**Environment Variables:**
- `DATA_DIR` — Output directory (default: "data")
- `TARGET_OBJECT` — Object designation (default: "3I/ATLAS")
- `SBDB_API_URL` — NASA SBDB API endpoint
- `HTTP_TIMEOUT_SEC` — Request timeout (default: 30)

**Exit Codes:**
- `0` — Success, data acquired
- `2` — SBDB error but snapshot written
- `3` — Other error or write failure

**Output Files:**
- `official_snapshot_{slug}_{timestamp}.json` — Timestamped SNAPSHOT
- `official_snapshot_latest.json` — Latest SNAPSHOT
- `platforms_registry_{timestamp}.json` — Platform registry DERIVED data

All files include TRIZEL metadata with checksums.

---

### 2. `metadata_enforcer.py` — Metadata Classification & Enforcement

**Purpose:** Classify existing data files and add/update metadata

**Features:**
- Automatic file classification (RAW_DATA, SNAPSHOT, DERIVED)
- Metadata schema enforcement
- SHA-256 checksum computation
- Manifest generation
- Validation against metadata schema

**Usage:**
```bash
python src/metadata_enforcer.py
```

**Classification Rules:**
- `jpl_sbdb_*.json` → RAW_DATA (NASA/JPL)
- `official_snapshot_*.json` → SNAPSHOT
- `platforms_registry_*.json` → DERIVED
- `latest_*.json` → SNAPSHOT

**Output:**
- Updates all JSON files with `trizel_metadata`
- Generates `data/DATA_MANIFEST.json`
- Prints statistics and validation results

**Exit Codes:**
- `0` — All files processed and validated
- `1` — Validation errors detected

---

### 3. `metadata_validator.py` — Metadata Schema Validation

**Purpose:** Validate metadata compliance for CI/CD enforcement

**Features:**
- Schema validation against METADATA_SCHEMA.md
- Agency whitelist enforcement
- Data class rule validation
- Checksum format verification
- ISO-8601 timestamp validation
- Manifest integrity checking

**Usage:**
```bash
python src/metadata_validator.py
```

**Validation Checks:**
1. Required fields present
2. Data class valid (RAW_DATA, SNAPSHOT, DERIVED)
3. Source agency whitelisted
4. RAW_DATA from official space agency (not INTERNAL)
5. Timestamp format ISO-8601 UTC
6. Checksum format valid
7. SNAPSHOT has source_raw_data
8. DERIVED has processing_pipeline
9. Manifest structure valid

**Exit Codes:**
- `0` — All validations passed
- `1` — Validation failures detected

**CI Integration:**
Used in `.github/workflows/metadata-validation.yml` to enforce compliance on push/PR.

---

## Metadata Schema

All data files must comply with TRIZEL Monitor Metadata Schema v1.0.0.

**Required Fields:**
```json
{
  "trizel_metadata": {
    "data_class": "RAW_DATA|SNAPSHOT|DERIVED",
    "source_agency": "NASA|ESA|CNSA|Roscosmos|JAXA|MPC|INTERNAL",
    "agency_endpoint": "https://...",
    "retrieval_timestamp_utc": "2026-01-10T17:00:00Z",
    "raw_release_policy": "NASA_OPEN_DATA|DERIVED_WORK|...",
    "checksum": "sha256:abc123...",
    "license": "CC0-1.0|CC-BY-4.0|...",
    "verification_status": "VERIFIED|PENDING|UNVERIFIED|FAILED",
    "schema_version": "1.0.0",
    "last_metadata_update_utc": "2026-01-10T17:00:00Z"
  },
  "data": { ... }
}
```

**See:** `METADATA_SCHEMA.md` for complete specification.

---

## Workflow Integration

### Daily Data Acquisition

The `daily.yml` workflow runs `main.py` automatically:
- Scheduled: Daily at 02:15 UTC
- Manual trigger: workflow_dispatch
- Commits new snapshots to repository

### Metadata Validation

The `metadata-validation.yml` workflow runs `metadata_validator.py`:
- On push to main (data/ changes)
- On pull requests
- Manual trigger: workflow_dispatch
- Fails CI if validation errors detected

---

## Development Guidelines

### Adding New Data Sources

1. Update whitelisted agencies in validators if needed
2. Add classification rules to `metadata_enforcer.py`
3. Update `main.py` to fetch from new source
4. Use `write_json_with_metadata()` for new files
5. Run `metadata_validator.py` to verify compliance

### Modifying Metadata Schema

1. Update `METADATA_SCHEMA.md` specification
2. Increment `schema_version`
3. Update validators and enforcers
4. Re-run `metadata_enforcer.py` on all files
5. Update CI workflows if needed

### Testing Changes

```bash
# Test data acquisition
python src/main.py

# Enforce metadata on existing files
python src/metadata_enforcer.py

# Validate all files
python src/metadata_validator.py

# Check Python syntax
python -m py_compile src/*.py
```

---

## Troubleshooting

### Validation Failures

If `metadata_validator.py` reports errors:
1. Check error messages for missing fields
2. Run `metadata_enforcer.py` to auto-fix
3. Manually inspect problematic files
4. Ensure compliance with METADATA_SCHEMA.md

### Classification Issues

If files are misclassified:
1. Check filename patterns in `metadata_enforcer.py`
2. Add new classification rules if needed
3. Re-run enforcer after updates

### CI Failures

If CI metadata validation fails:
1. Pull latest code
2. Run `metadata_validator.py` locally
3. Fix reported errors
4. Commit and push
5. CI will re-run validation

---

## Security

- All files checksummed with SHA-256
- CodeQL security scanning: No alerts
- No secrets in code
- Public domain (NASA) or CC-BY-4.0 licenses
- Read-only data consumption pattern

---

## References

- **METADATA_SCHEMA.md** — Metadata specification
- **DATA_CONTRACT.md** — Data contract and guarantees
- **ZENODO_MANIFEST.md** — Archival guidelines
- **VALIDATION_SUMMARY.md** — Audit compliance report

---

## Support

- **Repository:** https://github.com/abdelkader-omran/trizel-monitor
- **Issues:** Use GitHub Issues
- **Data Integrity:** Monitored via CI/CD

---

**Last Updated:** 2026-01-10  
**Schema Version:** 1.0.0
