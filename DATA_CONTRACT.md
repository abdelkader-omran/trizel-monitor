# DATA_CONTRACT.md  
**TRIZEL Monitor — Official Data Contract**

---

## 1. Purpose (Normative)

This document defines the **formal data contract** for the TRIZEL Monitor project.

Its purpose is to specify, in an unambiguous and machine-agnostic manner:

- What data is produced by the system
- How that data is structured
- What guarantees are provided
- What is explicitly out of scope

This contract applies to **all current and future versions** of the TRIZEL Monitor data-acquisition pipeline unless a new major version of this contract is published.

---

## 2. Scope and Non-Scope

### 2.1 In Scope

The system SHALL:

1. Acquire authoritative public data from the NASA/JPL SBDB API.
2. Persist immutable, timestamped snapshots of retrieved data.
3. Persist a stable `latest` snapshot reflecting the most recent run.
4. Persist a versioned registry of official scientific platforms.
5. Record retrieval metadata sufficient for audit, replication, and provenance.

### 2.2 Explicitly Out of Scope

The system SHALL NOT:

- Perform any physical interpretation or classification.
- Apply scientific inference, hypothesis testing, or modeling.
- Modify, normalize, or reinterpret authoritative source data.
- Merge, enrich, or correlate data across external sources.
- Make claims regarding the physical nature of any observed object.

All such activities belong to **downstream analytical frameworks** and are not part of this contract.

---

## 3. Authoritative Sources

The following sources are considered **authoritative inputs**:

- NASA/JPL Small-Body Database (SBDB) API  
  URL: https://ssd-api.jpl.nasa.gov/sbdb.api

The system MAY reference additional official platforms **only as registry entries** without automated data ingestion.

---

## 4. Target Object Semantics

### 4.1 Requested Designation

- The input designation (e.g., `"3I/ATLAS"`) SHALL be treated strictly as an:
  **archival and observational identifier**.
- It SHALL NOT imply physical classification, origin, or nature.

### 4.2 Resolved Designation

- If the authoritative payload contains an official designation,
  it SHALL be extracted verbatim.
- Resolution logic SHALL be passive and non-inferential.
- Both identifiers SHALL be preserved independently.

---

## 5. Output Artifacts

Each execution of the pipeline SHALL attempt to produce **three artifacts**:

1. **Timestamped Snapshot**
2. data/official_snapshot__<UTC_TIMESTAMP>.json
 2. **Latest Snapshot**
   data/official_snapshot_latest.json
 3. **Platforms Registry Snapshot**
  data/platforms_registry_<UTC_TIMESTAMP>.json
  Failure to write any artifact SHALL be treated as a fatal error.

---

## 6. Output Schema (Normative)

Each snapshot JSON file SHALL conform to the following top-level schema:

```json
{
"metadata": { ... },
"platforms_registry": { ... },
"sbdb_data": { ... },
"sbdb_error": null | { ... }
}
6.1 Metadata Object

The metadata object SHALL contain:
	•	project (string)
	•	pipeline (string)
	•	source (string)
	•	requested_designation (string)
	•	resolved_designation (string | null)
	•	retrieved_utc (ISO-8601 UTC string)
	•	run_id (string | null)
	•	retrieval_parameters (object)
	•	integrity (object)

6.2 sbdb_data
	•	SHALL always be a JSON object.
	•	SHALL be empty {} if no valid payload was retrieved.
	•	SHALL contain the raw SBDB payload when available.
	•	SHALL NOT be null.

6.3 sbdb_error
	•	SHALL be null on successful retrieval.
	•	SHALL be an object when any error occurs.
	•	SHALL include at minimum:
	•	type
	•	message
7. Error Classification Contract

The following error types are defined:
Error Type
Meaning
sbdb_error_payload
Authoritative SBDB returned a valid JSON error payload
http_error
HTTP status ≥ 400 without explicit SBDB error payload
request_exception
Network or transport failure
json_decode_error
Response body not valid JSON
8. Exit Code Semantics (Deterministic)

The process SHALL exit with exactly one of the following codes:
Exit Code
Condition
0
Successful completion, no errors
2
sbdb_error.type == "sbdb_error_payload"
3
Any other error OR filesystem/write failure
Exit codes SHALL NOT vary across versions unless this contract is versioned.

⸻

9. Write Guarantees
	•	All output files SHALL be written using atomic write semantics.
	•	Partial or corrupted files SHALL NOT be left on disk.
	•	Failure during write SHALL terminate execution with exit code 3.

⸻

10. Immutability and Reproducibility
	•	Timestamped snapshots are immutable by definition.
	•	The latest snapshot MAY change between runs.
	•	Historical snapshots SHALL remain unchanged once written.
	•	Given identical inputs and environment, outputs SHALL be reproducible.

⸻

11. Versioning Policy
	•	This contract is version-agnostic to code changes.
	•	Any breaking change to schema, semantics, or guarantees SHALL require:
	•	A new major version of this document
	•	Explicit documentation of changes

⸻

12. Contract Authority

This document is the authoritative specification for:
	•	Data consumers
	•	Reviewers
	•	Archival platforms (Zenodo, OSF, HAL)
	•	Automated validation and CI pipelines

In case of conflict between code comments and this document,
this document takes precedence.

⸻

13. Metadata Requirements (Mandatory)

All data artifacts produced by this system **MUST** include the following metadata fields:

### 13.1 Required Metadata Schema

Each data file SHALL contain a `trizel_metadata` object with:

- **data_class** (string, enum): One of `RAW_DATA`, `SNAPSHOT`, `DERIVED`
- **source_agency** (string): Official space agency or `INTERNAL`
- **agency_endpoint** (string): Verifiable API endpoint or data source
- **retrieval_timestamp_utc** (string): ISO-8601 UTC timestamp
- **raw_release_policy** (string): Data release policy
- **checksum** (string): Format `algorithm:hash` (e.g., `sha256:abc123...`)
- **license** (string): Data license (e.g., `CC0-1.0`, `CC-BY-4.0`)
- **verification_status** (string, enum): One of `VERIFIED`, `PENDING`, `UNVERIFIED`, `FAILED`

### 13.2 Whitelisted Space Agencies

RAW_DATA may ONLY originate from:
- NASA (United States)
- ESA (European Space Agency)
- CNSA (China National Space Administration)
- Roscosmos (Russian Space Agency)
- JAXA (Japan Aerospace Exploration Agency)
- MPC (Minor Planet Center - IAU)

### 13.3 Classification Rules

- **RAW_DATA**: Unmodified data from official space agencies
  - MUST have whitelisted `source_agency`
  - MUST have verifiable `agency_endpoint`
  - MUST have `verification_status: "VERIFIED"`

- **SNAPSHOT**: Timestamped system state captures
  - MUST reference at least one RAW_DATA source
  - MAY have `source_agency: "INTERNAL"`

- **DERIVED**: Processed or computed data
  - MUST include `processing_pipeline` field
  - MUST document source data

### 13.4 Validation and Enforcement

- Metadata compliance is enforced via CI/CD
- Files lacking required metadata WILL fail validation
- No manual override permitted
- See `METADATA_SCHEMA.md` for complete specification

### 13.5 Archival Manifest

The system SHALL generate a machine-readable manifest:
- File: `data/DATA_MANIFEST.json`
- Contains: Classification, checksums, statistics
- Updated: On every metadata enforcement run

⸻

14. Zenodo Archival Alignment

For long-term scientific archival (e.g., Zenodo):

### 14.1 Archive Organization

Zenodo releases SHALL clearly distinguish:
- **RAW DATA archives** — Original agency data
- **SNAPSHOT collections** — Timestamped aggregations
- **DERIVED datasets** — Processed outputs

### 14.2 DOI Continuity

- No deletion of published DOIs
- No overwrite of existing records
- Versioning through Zenodo's version mechanism
- Each version preserves data classification metadata

### 14.3 Archive Metadata

Each Zenodo record SHALL include:
- Reference to `DATA_MANIFEST.json`
- Clear indication of data_class for all files
- Links to original agency sources for RAW_DATA
- Checksums for integrity verification

⸻

15. Downstream Safety

### 15.1 Read-Only Consumption

Downstream repositories (e.g., AUTO-DZ-ACT-3I-ATLAS-DAILY) SHALL:
- Consume data in read-only mode
- NOT reclassify RAW_DATA as SNAPSHOT or DERIVED
- NOT modify metadata fields
- Preserve provenance chain

### 15.2 Immutable Classification

Once a file is classified as RAW_DATA and verified:
- Classification CANNOT be changed downstream
- Metadata MUST be preserved
- Checksums MUST remain valid

⸻

16. End of Contract

This file intentionally contains no executable logic.

It exists solely to define guarantees, constraints, and meaning.
