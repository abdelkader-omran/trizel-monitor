# PROJECT_STATUS.md

**AUTO DZ ACT — Component Status Tracker**

This document tracks the completion status of AUTO DZ ACT components with evidence-based verification.

---

## Status Definitions

- **COMPLETE**: Fully implemented and tested with verifiable evidence
- **PARTIAL**: Partially implemented or evidence incomplete
- **MISSING**: Not yet implemented

---

## Component Status Table

| Component | Status | Evidence |
|-----------|--------|----------|
| Zenodo DOI Registry | COMPLETE | ZENODO_INDEX.md with 9 explicit DOIs |
| RAW Ingest Contract Documentation | PARTIAL | DATA_CONTRACT.md § 13 (needs Zenodo-specific extension) |
| Timestamp Utilities | COMPLETE | src/utils/timestamps.py with now_utc_iso() |
| Hashing Utilities | COMPLETE | src/utils/hashing.py with sha256_file() and size_bytes() |
| Zenodo Fetch Module | MISSING | src/ingest/zenodo_fetch.py not yet created |
| Zenodo Ingest Entrypoint | MISSING | src/ingest/ingest_entrypoint.py not yet created |
| Horizons Ingest | COMPLETE | tools/fetch_horizons.py with RAW writer contract |
| RAW Path Ignoring | COMPLETE | .gitignore includes data/raw/ |
| Ingest Tests | PARTIAL | tests/test_ingest.py exists for Horizons, Zenodo tests missing |
| State Engine Scaffold | MISSING | src/logic/state_engine.py not yet created |
| Verification Scaffold | MISSING | src/logic/verification.py not yet created |

---

## Evidence Sources

All evidence must reference one of:
1. Explicit DOI from ZENODO_INDEX.md
2. Actual file path in repository
3. Actual RAW record path under data/raw/

No invented or speculative evidence is permitted.

---

## Last Updated

2025-12-21 (Auto-generated during initial scaffold)
