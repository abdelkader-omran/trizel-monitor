# DATA_CONTRACT.md  
**TRIZEL Monitor — Official Data Contract**

**Version:** 2.0.0  
**Status:** AUTHORITATIVE  
**Last Updated:** 2026-01-10

---

## 1. Purpose (Normative)

This document defines the **formal data contract** for the TRIZEL Monitor project.

Its purpose is to specify, in an unambiguous and machine-agnostic manner:

- What data is produced by the system
- How that data is structured (SINGLE METADATA BLOCK ONLY)
- What guarantees are provided
- What is explicitly out of scope
- How data is classified (RAW_DATA, SNAPSHOT, DERIVED)
- Checksum and integrity requirements (SHA-256 ONLY)

This contract applies to **all current and future versions** of the TRIZEL Monitor data-acquisition pipeline unless a new major version of this contract is published.

**This document supersedes all previous data contracts and issue-based specifications.**

---

## 2. Scope and Non-Scope

### 2.1 In Scope

The system SHALL:

1. Acquire data from authoritative space agency sources (NASA, ESA, JAXA, MPC only).
2. Persist immutable, timestamped snapshots with strict classification (RAW_DATA, SNAPSHOT, DERIVED).
3. Persist a stable `latest` snapshot reflecting the most recent run.
4. Compute and store SHA-256 checksums for all data files.
5. Record complete metadata in a SINGLE `trizel_metadata` block.
6. Provide visual attributes for data classification differentiation.
7. Enforce data governance rules via automated validation.

### 2.2 Explicitly Out of Scope

The system SHALL NOT:

- Perform any physical interpretation or classification of observed objects.
- Apply scientific inference, hypothesis testing, or modeling.
- Modify, normalize, or reinterpret authoritative source data.
- Merge, enrich, or correlate data across external sources.
- Make claims regarding the physical nature of any observed object.
- Use MD5 checksums (FORBIDDEN - cryptographically broken).

All such activities belong to **downstream analytical frameworks** and are not part of this contract.

---

## 3. Authoritative Sources (STRICT)

The following sources are the ONLY recognized **authoritative inputs**:

| Agency | Full Name                                | Role                          | Allowed Types     |
|--------|------------------------------------------|-------------------------------|-------------------|
| NASA   | National Aeronautics and Space Admin     | Space missions & archives     | RAW_DATA, SNAPSHOT|
| ESA    | European Space Agency                    | Space missions & archives     | RAW_DATA, SNAPSHOT|
| JAXA   | Japan Aerospace Exploration Agency       | Space missions & archives     | RAW_DATA, SNAPSHOT|
| MPC    | Minor Planet Center (IAU)                | Astrometry & orbit registry   | RAW_DATA, SNAPSHOT|

**NASA/JPL SBDB API:** https://ssd-api.jpl.nasa.gov/sbdb.api (SNAPSHOT only - computed values)

The system SHALL NOT accept data from any other source. Validation MUST fail if an unsupported agency is used.

---

## 4. Data Classification Rules (MANDATORY)

### 4.1 RAW_DATA Requirements

Data MAY ONLY be classified as `RAW_DATA` if ALL conditions are met:

1. **Source is official agency:** NASA, ESA, JAXA, or MPC only
2. **Direct download:** Original files from archival systems (not API summaries)
3. **Explicit provenance:** Source URL, checksum, and release policy documented

### 4.2 SNAPSHOT Data

API responses, computed orbital elements, and real-time queries MUST be classified as `SNAPSHOT`:

- JPL SBDB API responses → SNAPSHOT (NOT RAW_DATA)
- Real-time computed values → SNAPSHOT
- Summary statistics → SNAPSHOT

Visual: Orange / ⚠ / "SNAPSHOT – NO SCIENTIFIC VALUE ALONE"

### 4.3 DERIVED Data

Processed, analyzed, or transformed data MUST be classified as `DERIVED`:

- Analysis results → DERIVED
- Computed metrics → DERIVED
- Visualizations → DERIVED

Visual: Blue / → / "DERIVED DATA"

### 4.4 Classification Enforcement

- CI validation MUST fail if RAW_DATA rules are violated
- All data files MUST include correct classification
- Visual attributes MUST match classification

---

## 5. Target Object Semantics

### 5.1 Requested Designation

- The input designation (e.g., `"3I/ATLAS"`) SHALL be treated strictly as an:
  **archival and observational identifier**.
- It SHALL NOT imply physical classification, origin, or nature.

### 5.2 Resolved Designation

- If the authoritative payload contains an official designation,
  it SHALL be extracted verbatim.
- Resolution logic SHALL be passive and non-inferential.
- Both identifiers SHALL be preserved independently.

---

## 6. Output Schema (Normative)

### 6.1 Mandatory Structure

Each data file SHALL conform to the following schema with EXACTLY ONE metadata block:

```json
{
  "trizel_metadata": {
    "project": "TRIZEL Monitor",
    "pipeline": "string - pipeline name",
    "version": "1.0.0",
    "data_classification": "RAW_DATA | SNAPSHOT | DERIVED",
    "source_agency": "NASA | ESA | JAXA | MPC",
    "query_designation": "string - requested object name",
    "resolved_designation": "string | null - API-returned designation",
    "retrieved_utc": "ISO-8601 UTC string",
    "checksum": {
      "algorithm": "sha256 | sha512",
      "value": "hex string - required"
    },
    "provenance": {
      "source_url": "string - API endpoint or archive URL",
      "source_type": "api | archive | download",
      "release_policy": "string - data release information"
    },
    "visual_attributes": {
      "color": "green | orange | blue",
      "icon": "✓ | ⚠ | →",
      "label": "RAW DATA | SNAPSHOT – NO SCIENTIFIC VALUE ALONE | DERIVED DATA"
    },
    "integrity": {
      "has_data_payload": "boolean",
      "has_error": "boolean",
      "validation_status": "string"
    }
  },
  "data": {
    // Actual data payload - MAY be empty object {} on error
  }
}
```

### 6.2 Metadata Block Rules (CI-ENFORCED)

1. **EXACTLY ONE metadata block:** `trizel_metadata` MUST appear ONCE at root level
2. **NO nested metadata:** No duplicated metadata blocks at any depth
3. **NO legacy keys:** Keys like `metadata`, `platforms_registry`, `sbdb_data`, `sbdb_error` are FORBIDDEN at root level
4. **ALL required fields:** Every field listed above MUST be present
5. **Type enforcement:** All fields MUST match specified types

### 6.3 Data Object

- SHALL always be a JSON object
- SHALL be empty `{}` if no valid payload was retrieved
- SHALL contain the raw payload when available
- SHALL NOT be null
---

## 7. Checksum Policy (MANDATORY)

### 7.1 Required Algorithm

- **SHA-256:** REQUIRED for all data files
- Checksum MUST be computed over the entire file content
- Checksum MUST be stored in `trizel_metadata.checksum.value`

### 7.2 Optional Algorithm

- **SHA-512:** OPTIONAL, may be provided in `trizel_metadata.checksum.sha512`

### 7.3 Forbidden Algorithms

- **MD5:** ABSOLUTELY FORBIDDEN (cryptographically broken)
- Any code or data file using MD5 MUST cause CI to fail

### 7.4 Checksum Verification

- All data files MUST include a valid SHA-256 checksum
- Validation scripts MUST verify checksums match file content
- Mismatched checksums MUST cause validation to fail

---

## 8. Visual Attributes (REQUIRED)

Every data file MUST include visual_attributes for UI/tool rendering:

| Classification | color  | icon | label                                  |
|----------------|--------|------|----------------------------------------|
| RAW_DATA       | green  | ✓    | RAW DATA                               |
| SNAPSHOT       | orange | ⚠    | SNAPSHOT – NO SCIENTIFIC VALUE ALONE   |
| DERIVED        | blue   | →    | DERIVED DATA                           |

Purpose:
- Clear visual distinction in dashboards and tools
- Semantic clarity for data consumers
- Scientific integrity in labeling (no misleading classifications)

---

## 9. Error Classification Contract

When data retrieval fails, errors SHALL be classified as:

| Error Type            | Meaning                                          |
|-----------------------|--------------------------------------------------|
| api_error_response    | Authoritative API returned valid JSON error      |
| http_error            | HTTP status ≥ 400 without API error payload      |
| request_exception     | Network or transport failure                     |
| json_decode_error     | Response body not valid JSON                     |
| validation_error      | Data validation failed                           |

Errors SHALL be stored in `trizel_metadata.integrity.has_error` and detailed separately.
---

## 10. Exit Code Semantics (Deterministic)

The process SHALL exit with exactly one of the following codes:

| Exit Code | Condition                                        |
|-----------|--------------------------------------------------|
| 0         | Successful completion, no errors                 |
| 1         | Validation failure (schema, classification, etc) |
| 2         | API error (authoritative source returned error)  |
| 3         | Network/filesystem/write failure                 |

Exit codes SHALL NOT vary across versions unless this contract is versioned.

---

## 11. Write Guarantees

- All output files SHALL be written using atomic write semantics.
- Partial or corrupted files SHALL NOT be left on disk.
- Failure during write SHALL terminate execution with exit code 3.
- All files MUST be valid JSON and parseable.

---

## 12. Immutability and Reproducibility

- Timestamped snapshots are immutable by definition.
- The latest snapshot MAY change between runs.
- Historical snapshots SHALL remain unchanged once written.
- Given identical inputs and environment, outputs SHALL be reproducible.
- Checksums ensure data integrity across storage and transmission.

---

## 13. Validation Requirements (CI-ENFORCED)

### 13.1 Automated Validation

CI MUST validate ALL data files for:

1. **Single metadata block:** Exactly one `trizel_metadata` at root
2. **No duplicates:** No nested or duplicated metadata blocks
3. **RAW_DATA rules:** Classification matches source type and agency
4. **Agency whitelist:** Only NASA, ESA, JAXA, MPC allowed
5. **Checksum policy:** SHA-256 present, no MD5
6. **Visual attributes:** Present and match classification
7. **Required fields:** All mandatory fields present
8. **Type correctness:** All fields match specified types

### 13.2 Validation Failures

ANY of the following MUST cause validation to fail:

- Multiple metadata blocks
- RAW_DATA misclassification (API data marked as RAW_DATA)
- Unsupported agency
- MD5 checksum anywhere in codebase or data
- Missing required fields
- Invalid field types
- Missing visual attributes
- Checksum mismatch

---

## 14. Versioning Policy

- This contract is version 2.0.0 (major update from 1.x)
- Breaking changes from 1.x:
  - Single `trizel_metadata` block (was `metadata`)
  - Mandatory data classification
  - SHA-256 checksums required
  - Visual attributes required
  - Strict agency whitelist
- Any breaking change to schema, semantics, or guarantees SHALL require:
  - A new major version of this document
  - Explicit documentation of changes
  - Migration guide for existing data

---

## 15. Contract Authority

This document is the authoritative specification for:

- Data producers and consumers
- Code reviewers
- Archival platforms (Zenodo, OSF, HAL)
- Automated validation and CI pipelines
- Scientific integrity verification

In case of conflict between code comments and this document,
**this document takes precedence**.

---

## 16. End of Contract

This file intentionally contains no executable logic.

It exists solely to define guarantees, constraints, and meaning.

**All implementations MUST conform to this specification.**
