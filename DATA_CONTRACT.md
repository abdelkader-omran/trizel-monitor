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

## 13. RAW Ingest Contract (Phase 2 Extension)

### 13.1 Purpose

This section extends the TRIZEL Monitor data contract to include the **RAW ingest layer**, which provides append-only, immutable storage for all ingested data artifacts.

### 13.2 Directory Structure

All RAW ingest SHALL follow this structure:

```
data/raw/<YYYY-MM-DD>/<SOURCE_ID>/<DATASET_KEY>/
  records/
    <record_id>.json
  payload/
    <record_id>__payload.json
```

Where:
- `<YYYY-MM-DD>` is the UTC date of ingestion
- `<SOURCE_ID>` identifies the data source (e.g., "horizons", "zenodo_<DOI_SUFFIX>")
- `<DATASET_KEY>` identifies the dataset type (e.g., "snapshot")
- `<record_id>` is a unique UUID v4 identifier

### 13.3 Record Metadata Schema

Each `records/<record_id>.json` file SHALL contain:

```json
{
  "record_id": "<UUID>",
  "retrieved_utc": "<ISO-8601 UTC with timezone>",
  "provenance": {
    "source": "<source_identifier>",
    ...additional source-specific fields
  },
  "sha256": "<hex_digest>",
  "size_bytes": <integer>,
  "payload_path": "payload/<record_id>__payload.json"
}
```

**Required Fields:**
- `record_id` (string): Unique identifier for this record
- `retrieved_utc` (string): Timezone-aware UTC timestamp (ISO-8601)
- `provenance` (object): Source metadata
- `sha256` (string): SHA-256 hash of payload bytes
- `size_bytes` (integer): Size of payload in bytes
- `payload_path` (string): Relative path to payload file

**Provenance Requirements:**

For Zenodo sources:
```json
"provenance": {
  "source": "zenodo",
  "doi": "<DOI>",
  "version": "<version_if_available>",
  ...
}
```

For offline files:
```json
"provenance": {
  "source": "offline_file",
  "input_file": "<absolute_path>",
  "ingested_at": "<ISO-8601_UTC>"
}
```

### 13.4 Immutability Guarantees

1. **No Overwrites**: If a `record_id` collision occurs, a new UUID SHALL be generated
2. **Append-Only**: Existing records SHALL never be modified
3. **Integrity**: `sha256` and `size_bytes` SHALL be computed from actual payload bytes on disk
4. **Deterministic Paths**: Directory structure SHALL be deterministic based on date and source

### 13.5 Collision Handling

When generating a `record_id`:
1. Generate a UUID v4
2. Check if `records/<record_id>.json` OR `payload/<record_id>__payload.json` exists
3. If either exists, regenerate UUID and retry
4. Maximum retry attempts: 100
5. If max attempts exceeded, fail with error

### 13.6 Dry-Run Mode

Ingest tools SHALL support `--output-only` mode that:
- Reads and validates input
- Computes intended paths and metadata
- Prints planned actions
- Does NOT write any files

### 13.7 Error Handling

All ingest failures SHALL emit:
- At least one `[ERROR]` line describing the failure
- 1-3 `[HINT]` lines providing actionable guidance
- Non-zero exit code

### 13.8 Zenodo-Specific Extensions

**CLI Contract:**
```bash
python src/ingest/ingest_entrypoint.py --source zenodo --doi <DOI> --mode ingest [--input <path>] [--output-only]
```

**Source ID Format:**
- For Zenodo records: `zenodo_<DOI_SUFFIX>`
- Example: DOI `10.5281/zenodo.16292189` → `zenodo_16292189`

**Provenance Schema for Zenodo:**
```json
{
  "source": "zenodo",
  "doi": "<full_DOI>",
  "version": "<version_string_or_unknown>"
}
```

**Recognized Zenodo DOIs:**
All Zenodo ingests MUST reference one of the explicit DOIs listed in `ZENODO_INDEX.md`. No DOI inference is permitted.

**Offline-First Rule:**
- If `--input` is provided, use offline file and do NOT require network
- If `--input` is not provided, attempt online fetch via Zenodo API
- Network failures MUST emit graceful [ERROR] and [HINT] messages

⸻

14. End of Contract

This file intentionally contains no executable logic.

It exists solely to define guarantees, constraints, and meaning.
