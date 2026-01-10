# TRIZEL Raw Data Governance & Archival Integrity Framework (Authoritative)

**Status:** AUTHORITATIVE - This is the ONLY reference for raw data ingestion, classification, validation, and archival policy.

**Date Created:** 2026-01-10

---

## Purpose

This issue consolidates and supersedes ALL previous fragmented issues related to data acquisition, ingestion, and governance. It establishes a single, coherent, enforceable framework for scientific data management in the TRIZEL Monitor project.

---

## Superseded Issues

This authoritative issue **REPLACES** the following issues, which are now closed and marked as redundant:

- **Issue #1:** [WIP] Implement a data acquisition tool for NASA JPL Horizons API
- **Issue #2:** Implement JPL Horizons data acquisition with offline mode and integrity verification
- **Issue #3:** Add --mode ingest for additive-only RAW record ingestion
- **Issue #4:** Add --mode ingest for RAW record acquisition with offline-first execution
- **Issue #5:** Add Phase 2 RAW ingest layer with Horizons + Zenodo offline-first ingestion
- **Issue #6:** TRIZEL Scientific Ingest Layer – Comprehensive Local Scan & Verification Report

**Reason for Supersession:** These issues fragmented the scientific data model and created overlapping, inconsistent implementations. This framework provides a unified, authoritative specification.

---

## 1. Single Scientific Data Model

### 1.1 Mandatory Structure

Every data file MUST conform to the following structure:

```json
{
  "trizel_metadata": {
    "project": "TRIZEL Monitor",
    "pipeline": "string",
    "version": "1.0.0",
    "data_classification": "RAW_DATA | SNAPSHOT | DERIVED",
    "source_agency": "NASA | ESA | JAXA | MPC",
    "retrieved_utc": "ISO-8601 timestamp",
    "checksum": {
      "sha256": "required hex string",
      "sha512": "optional hex string"
    },
    "provenance": {
      "source_url": "string",
      "source_type": "api | archive | download",
      "release_policy": "string"
    },
    "visual_attributes": {
      "color": "green | orange | blue",
      "icon": "✓ | ⚠ | →",
      "label": "RAW DATA | SNAPSHOT – NO SCIENTIFIC VALUE ALONE | DERIVED DATA"
    }
  },
  "data": {
    // Actual data payload
  }
}
```

### 1.2 Invariants (CI-Enforced)

1. **Exactly ONE metadata block:** `trizel_metadata` MUST appear ONCE and ONLY ONCE at the root level
2. **No nested metadata:** No duplicated metadata blocks at any depth
3. **No missing metadata:** All required fields MUST be present
4. **Strict typing:** All fields MUST match their specified types

---

## 2. RAW_DATA Classification Rules (STRICT)

### 2.1 Requirements for RAW_DATA

Data MAY ONLY be classified as `RAW_DATA` if ALL of the following conditions are met:

1. **Official Source:** Data originates from an official space agency archive:
   - NASA (National Aeronautics and Space Administration)
   - ESA (European Space Agency)
   - JAXA (Japan Aerospace Exploration Agency)
   - MPC (Minor Planet Center)

2. **Direct Download:** Data is directly downloadable as original files, NOT API summaries or computed values

3. **Explicit Provenance:** Source URL, checksum, and release delay policy are explicitly documented

### 2.2 Prohibited RAW_DATA Classifications

The following data types MUST NEVER be classified as `RAW_DATA`:

- **API Snapshots:** JPL SBDB API responses (computed orbital elements)
- **Derived Values:** Any computed, interpolated, or inferred data
- **Aggregated Data:** Summary statistics or combined datasets
- **Transformed Data:** Any data that has been processed or reformatted

### 2.3 Correct Classifications

- **SNAPSHOT:** Real-time API responses, computed orbital elements, summary data
  - Visual: Orange / ⚠ / "SNAPSHOT – NO SCIENTIFIC VALUE ALONE"
  - Use case: JPL SBDB API, real-time queries, status checks

- **DERIVED:** Processed, analyzed, or transformed data
  - Visual: Blue / → / "DERIVED DATA"
  - Use case: Analysis results, computed metrics, visualizations

- **RAW_DATA:** Original, unmodified archival files from official sources
  - Visual: Green / ✓ / "RAW DATA"
  - Use case: Downloaded FITS files, original observation data, archived telemetry

---

## 3. Checksum Policy (MANDATORY)

### 3.1 Allowed Algorithms

- **SHA-256:** REQUIRED for all data files
- **SHA-512:** OPTIONAL, may be provided for additional verification

### 3.2 Forbidden Algorithms

- **MD5:** FORBIDDEN (cryptographically broken, MUST NOT be used)

### 3.3 CI Enforcement

- Any data file or code that uses MD5 MUST cause CI to fail
- All data files MUST include a valid SHA-256 checksum
- Checksums MUST be verified during validation

---

## 4. Visual & Semantic Differentiation

Every data file MUST include `visual_attributes` block:

| Classification | Color  | Icon | Label                                  |
|----------------|--------|------|----------------------------------------|
| RAW_DATA       | green  | ✓    | RAW DATA                               |
| SNAPSHOT       | orange | ⚠    | SNAPSHOT – NO SCIENTIFIC VALUE ALONE   |
| DERIVED        | blue   | →    | DERIVED DATA                           |

These attributes ensure:
- Clear visual distinction in tools and UIs
- Semantic clarity for downstream consumers
- Scientific integrity in labeling

---

## 5. Supported Agencies

Only the following agencies are recognized as authoritative sources:

| Agency | Full Name                               | Role                        |
|--------|----------------------------------------|------------------------------|
| NASA   | National Aeronautics and Space Admin   | Space missions & archives    |
| ESA    | European Space Agency                  | Space missions & archives    |
| JAXA   | Japan Aerospace Exploration Agency     | Space missions & archives    |
| MPC    | Minor Planet Center (IAU)              | Astrometry & orbit registry  |

Use of any other agency MUST cause validation to fail.

---

## 6. Documentation Consolidation

All documentation MUST report consistent information:

- **README.md:** High-level overview, consistent terminology
- **DATA_CONTRACT.md:** Formal specification, schema definitions
- **MANIFEST files:** Accurate file counts, classifications

**Zero tolerance for inconsistencies.**

---

## 7. Validation Requirements

### 7.1 Automated Validation (CI)

CI MUST validate:

1. Metadata structure (single block, no duplicates)
2. RAW_DATA classification rules
3. Agency whitelist enforcement
4. Checksum policy compliance
5. Visual attributes presence and correctness
6. Required fields presence and types

### 7.2 Validation Failures

Any of the following MUST cause validation to fail:

- Duplicated metadata blocks
- RAW_DATA misclassification
- Unsupported agency
- MD5 checksum usage
- Missing required fields
- Invalid data types

---

## 8. Implementation Status

- [x] Authoritative issue created
- [ ] Data model implemented in code
- [ ] Validation script created
- [ ] CI workflow configured
- [ ] Documentation updated
- [ ] Existing data files migrated
- [ ] Full validation passing

---

## 9. Success Criteria

This implementation is complete when:

1. **One clean implementation:** Single, consistent codebase
2. **One authoritative issue:** This document (no others)
3. **Zero ambiguity:** Clear rules, no exceptions
4. **Zero scientific mislabeling:** All data correctly classified
5. **CI enforcement:** All rules automatically validated
6. **Documentation consistency:** All docs report same information

---

## 10. Maintenance

This document is the authoritative reference. Any changes to data governance MUST:

1. Update this document first
2. Update implementation to match
3. Update documentation to match
4. Verify CI enforcement

**No exceptions.**

---

## Contact

For questions or clarifications, refer to this document. It is the single source of truth.

**Status: READY**
