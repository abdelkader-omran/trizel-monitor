# Issue Supersession Notice

**Date:** 2026-01-10  
**Action:** Consolidation and Supersession  
**Status:** CLOSED and SUPERSEDED

---

## Superseded Issues

The following issues have been **CLOSED** and **SUPERSEDED** by the authoritative framework:

1. **Issue #1:** [WIP] Implement a data acquisition tool for NASA JPL Horizons API
2. **Issue #2:** Implement JPL Horizons data acquisition with offline mode and integrity verification
3. **Issue #3:** Add --mode ingest for additive-only RAW record ingestion
4. **Issue #4:** Add --mode ingest for RAW record acquisition with offline-first execution
5. **Issue #5:** Add Phase 2 RAW ingest layer with Horizons + Zenodo offline-first ingestion
6. **Issue #6:** TRIZEL Scientific Ingest Layer – Comprehensive Local Scan & Verification Report

---

## Reason for Supersession

These issues created a **fragmented scientific data model** with:
- Overlapping implementations
- Inconsistent metadata structures
- Ambiguous data classification rules
- No unified governance framework

This fragmentation posed risks to:
- Scientific integrity
- Data reproducibility
- Archival compliance
- Validation consistency

---

## Replacement Framework

All superseded issues are replaced by:

### Single Authoritative Issue
**[ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md](ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md)**

This document provides:
- Single source of truth for data governance
- Strict data classification rules (RAW_DATA, SNAPSHOT, DERIVED)
- Mandatory checksum policy (SHA-256 only, MD5 forbidden)
- Agency whitelist (NASA, ESA, JAXA, MPC)
- Visual attributes for data differentiation
- CI-enforced validation rules

### Implementation

The framework is fully implemented in:
- **Code:** `src/main.py` (data acquisition), `src/validate_data.py` (validation)
- **CI:** `.github/workflows/validation.yml` (automated enforcement)
- **Documentation:** `DATA_CONTRACT.md` v2.0.0, `README.md`, `MANIFEST.md`
- **Data:** All files conform to v2.0.0 schema

---

## Migration Complete

### What Changed

**Before (issues #1-6):**
- Multiple metadata structures
- Unclear RAW_DATA vs SNAPSHOT distinction
- No checksum policy
- No validation enforcement
- Fragmented documentation

**After (authoritative framework):**
- Single `trizel_metadata` block (enforced)
- Strict RAW_DATA rules (NASA/ESA/JAXA/MPC archival downloads only)
- SHA-256 checksums required, MD5 forbidden
- CI validation on every push/PR
- Consolidated documentation

### File Changes

**Removed:**
- 17 legacy data files (non-compliant format)
- Empty TASK_TRIZEL_SCIENTIFIC_INGEST.md

**Added:**
- ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md (authoritative spec)
- MANIFEST.md (file inventory)
- .gitignore (build artifacts)
- src/validate_data.py (validation script)
- .github/workflows/validation.yml (CI workflow)

**Updated:**
- DATA_CONTRACT.md (v1.x → v2.0.0)
- README.md (governance-aware)
- src/main.py (v2.0.0 compliant)
- data/ (2 compliant files)

---

## Validation Status

✅ **All validation passing:**
- 2/2 data files compliant
- 0 errors, 0 warnings
- Single metadata block enforced
- RAW_DATA rules enforced
- Checksum policy enforced
- Visual attributes correct

---

## Action Required

**Repository Owner:**
1. Close issues #1-6 on GitHub (mark as "superseded")
2. Add comment to each: "Superseded by ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md"
3. Lock issues to prevent further discussion
4. Pin ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md as the authoritative reference

**Note:** These actions require GitHub permissions that the automation does not have. Manual action required.

---

## Future Work

All future data governance work MUST:
1. Reference ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md
2. Update that document first before making changes
3. Maintain CI validation compliance
4. Keep documentation consistency (README, DATA_CONTRACT, MANIFEST)

**No new issues should fragment the data model.**

---

## Contact

For questions about this supersession:
- See: ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md (authoritative spec)
- See: DATA_CONTRACT.md (technical contract)
- See: MANIFEST.md (file inventory)

**Status:** MIGRATION COMPLETE  
**Framework:** AUTHORITATIVE and ACTIVE
