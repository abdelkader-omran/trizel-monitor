# METADATA SCHEMA — TRIZEL Monitor

## Purpose

This document defines the **mandatory metadata schema** for all data artifacts in the TRIZEL Monitor repository.

This schema enforces scientific integrity, raw data provenance, and archival traceability as required for international space agency data compliance.

---

## Scope

This schema applies to **ALL** data files in the repository, including:
- JSON files
- CSV files  
- TXT files
- Any future data formats

---

## Mandatory Metadata Fields

Every data artifact **MUST** contain the following fields:

### 1. data_class (REQUIRED)

**Type:** String (enum)  
**Allowed values:**
- `RAW_DATA` — Original data from official international space agencies
- `SNAPSHOT` — Timestamped capture of system state or aggregated data
- `DERIVED` — Computed, processed, or synthesized data

**Rules:**
- RAW_DATA may ONLY originate from whitelisted international space agencies
- SNAPSHOT must reference at least one RAW_DATA source
- DERIVED must document all source data and processing steps

### 2. source_agency (REQUIRED)

**Type:** String  
**Allowed values (whitelist):**
- `NASA` (United States)
- `ESA` (European Space Agency)
- `CNSA` (China National Space Administration)
- `Roscosmos` (Russian Space Agency)
- `JAXA` (Japan Aerospace Exploration Agency)
- `MPC` (Minor Planet Center - IAU)
- `INTERNAL` (for SNAPSHOT and DERIVED only)

**Rules:**
- For RAW_DATA: MUST be one of the whitelisted agencies
- For SNAPSHOT/DERIVED: Use `INTERNAL` or specify source if aggregating agency data

### 3. agency_endpoint (REQUIRED)

**Type:** String (URL or identifier)  
**Format:** Valid URL or official data identifier

**Examples:**
- `https://ssd-api.jpl.nasa.gov/sbdb.api`
- `https://minorplanetcenter.net/db_search`
- `INTERNAL_PIPELINE`

**Rules:**
- For RAW_DATA: Must be verifiable public endpoint or data repository
- For SNAPSHOT/DERIVED: Document source pipeline or aggregation endpoint

### 4. retrieval_timestamp_utc (REQUIRED)

**Type:** String (ISO-8601 UTC timestamp)  
**Format:** `YYYY-MM-DDTHH:MM:SSZ`

**Example:** `2025-12-21T03:45:14Z`

**Rules:**
- Must be in UTC timezone
- Must use ISO-8601 format
- For SNAPSHOT/DERIVED: Use generation timestamp

### 5. raw_release_policy (REQUIRED)

**Type:** String  
**Description:** Official data release policy or availability statement

**Examples:**
- `PUBLIC_DOMAIN` (NASA)
- `OPEN_DATA` (ESA)
- `RESTRICTED_EXPORT` (varies by agency)
- `DERIVED_WORK` (for processed data)

### 6. checksum (REQUIRED)

**Type:** String  
**Format:** `<algorithm>:<hash>`

**Example:** `sha256:a3b2c1d4e5f6...`

**Supported algorithms:**
- `sha256` (recommended)
- `md5` (legacy support)
- `sha512` (high security)

**Rules:**
- Must be computed over the entire file content
- Must be verifiable independently

### 7. license (REQUIRED)

**Type:** String  
**Allowed values:**
- `CC0-1.0` (Public Domain)
- `CC-BY-4.0` (Attribution required)
- `NASA-OPEN` (NASA Open Data Policy)
- `ESA-OPEN` (ESA Open Data Policy)
- `PROPRIETARY` (with justification)

### 8. verification_status (REQUIRED)

**Type:** String (enum)  
**Allowed values:**
- `VERIFIED` — Data source and provenance confirmed
- `PENDING` — Awaiting verification
- `UNVERIFIED` — Cannot verify source
- `FAILED` — Verification failed

**Rules:**
- RAW_DATA should be `VERIFIED` before publication
- SNAPSHOT/DERIVED can be `VERIFIED` if sources are verified

---

## Extended Metadata (RECOMMENDED)

### 9. object_designation (OPTIONAL)

**Type:** String  
**Description:** Official astronomical object designation

**Example:** `3I/ATLAS`

### 10. processing_pipeline (OPTIONAL for DERIVED)

**Type:** String  
**Description:** Name and version of processing pipeline

**Example:** `TRIZEL Monitor v1.0`

### 11. source_raw_data (REQUIRED for SNAPSHOT)

**Type:** Array of strings  
**Description:** References to raw data files used

**Example:** `["jpl_sbdb_20251218_191351.json"]`

### 12. zenodo_doi (OPTIONAL)

**Type:** String  
**Description:** Zenodo DOI for archival record

**Example:** `10.5281/zenodo.1234567`

---

## File-Specific Requirements

### RAW_DATA Files

Must include:
- `data_class: "RAW_DATA"`
- Whitelisted `source_agency`
- Verifiable `agency_endpoint`
- `verification_status: "VERIFIED"`

Must NOT include:
- Processing or transformation metadata
- Interpretation or analysis

### SNAPSHOT Files

Must include:
- `data_class: "SNAPSHOT"`
- `source_raw_data` array with at least one RAW_DATA reference
- `source_agency: "INTERNAL"` or aggregated agency list

### DERIVED Files

Must include:
- `data_class: "DERIVED"`
- `processing_pipeline` description
- Source data references (if applicable)

---

## Validation

All metadata MUST pass CI validation before merge.

Validation checks:
1. All required fields present
2. Field types correct
3. Enum values from allowed lists
4. Agency whitelist enforcement
5. Checksum verification
6. ISO-8601 timestamp format
7. RAW_DATA source verification

---

## Non-Compliance

Files lacking required metadata will:
- Fail CI validation
- Be flagged in automated audits
- Be excluded from Zenodo archival
- Not be considered scientifically valid

---

## Schema Version

**Version:** 1.0.0  
**Last Updated:** 2026-01-10  
**Authority:** TRIZEL Monitor Scientific Integrity Policy
