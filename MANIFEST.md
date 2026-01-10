# TRIZEL Monitor - File Manifest

**Version:** 3.0.0  
**Data Governance Version:** 3.0.0  
**Last Updated:** 2026-01-10

---

## Data Files

All data files follow the authoritative schema defined in DATA_CONTRACT.md.

### Current Inventory

| Filename | Classification | Agency | Type | Status |
|----------|---------------|--------|------|--------|
| snapshot_3I_ATLAS_latest.json | SNAPSHOT | NASA | Latest snapshot | Active |
| snapshot_3I_ATLAS_20260110_185404.json | SNAPSHOT | NASA | Timestamped snapshot | Active |
| snapshot_3I_ATLAS_20260110_185452.json | SNAPSHOT | NASA | Timestamped snapshot | Active |

**Total Data Files:** 3 (as of 2026-01-10)

### Classification Breakdown

- **RAW_DATA:** 0 files (direct archival downloads only)
- **SNAPSHOT:** 3 files (JPL SBDB API responses)
- **DERIVED:** 0 files (analysis results)

---

## Source Code

| File | Purpose |
|------|---------|
| src/main.py | Data acquisition from JPL SBDB API |
| src/validate_data.py | Data governance validation script |

---

## Documentation

| File | Purpose |
|------|---------|
| README.md | Project overview and usage |
| DATA_CONTRACT.md | Authoritative data contract (v2.0.0) |
| ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md | Complete governance framework |
| MANIFEST.md | This file - file inventory |

---

## Workflows

| File | Purpose |
|------|---------|
| .github/workflows/daily.yml | Daily data acquisition automation |
| .github/workflows/validation.yml | Data governance validation CI |

---

## Validation Status

All data files MUST pass validation against:

1. Single metadata block rule (trizel_metadata only)
2. RAW_DATA classification rules
3. Agency whitelist (NASA, ESA, JAXA, MPC)
4. Checksum policy (SHA-256 required, MD5 forbidden)
5. Visual attributes correctness

Run validation:
```bash
python src/validate_data.py
```

---

## Legacy Files (Removed)

The following legacy files were removed during governance consolidation:

- jpl_sbdb_*.json (non-compliant format)
- latest_jpl_sbdb.json (non-compliant format)
- official_snapshot_*.json (non-compliant format)
- platforms_registry_*.json (moved to code-based registry)

**Reason:** Did not conform to v2.0.0 data contract (missing trizel_metadata block, no checksums, no classification).

---

## File Naming Convention

- **Snapshots:** `snapshot_{OBJECT}_{TIMESTAMP}.json`
- **Latest:** `snapshot_{OBJECT}_latest.json`
- **Timestamp format:** `YYYYMMDD_HHMMSS` (UTC)

Examples:
- `snapshot_3I_ATLAS_20260110_181838.json`
- `snapshot_3I_ATLAS_latest.json`

---

## Checksums

All data files include SHA-256 checksums in their metadata:

```json
{
  "trizel_metadata": {
    "checksum": {
      "algorithm": "sha256",
      "value": "hex string (64 characters)"
    }
  }
}
```

Verify checksums during validation to ensure data integrity.

---

## Superseded Documentation

This manifest supersedes any previous inventory or file counting methods. All documentation (README.md, DATA_CONTRACT.md, MANIFEST.md) reports consistent numbers and classifications.

---

**Status:** CURRENT and AUTHORITATIVE
