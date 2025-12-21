# TASK_TRIZEL_SCIENTIFIC_INGEST.md

**TRIZEL Monitor — Scientific Data Ingest Task Documentation**

This document describes the data ingestion processes for the TRIZEL Monitor project.

---

## Horizons Ingest (Phase 2)

The Horizons ingest mode allows offline-first ingestion of JPL Horizons ephemeris data into the RAW data layer.

### Execution

```bash
# Using existing snapshot as input
python src/main.py --mode ingest

# Using specific offline file
python src/main.py --mode ingest --input <path_to_json>

# Dry-run mode
python tools/fetch_horizons.py --input <path> --output-only
```

### Output Structure

```
data/raw/<YYYY-MM-DD>/horizons/snapshot/
  records/<record_id>.json
  payload/<record_id>__payload.json
```

---

## Zenodo Ingest (AUTO DZ ACT Extension)

The Zenodo ingest mode provides append-only RAW storage for Zenodo records referenced in AUTO DZ ACT verification chains.

### Recognized DOIs

All Zenodo ingests must reference explicit DOIs listed in `ZENODO_INDEX.md`. Current recognized DOIs:

**Core Releases:**
- 10.5281/zenodo.16292189 — Initial logic
- 10.5281/zenodo.16336645 — V2 executable
- 10.5281/zenodo.16519770 — V2.0 base
- 10.5281/zenodo.16522543 — V2.1 enhanced logic
- 10.5281/zenodo.17968772 — V2.2 (3I/ATLAS)
- 10.5281/zenodo.17968771 — Latest resolver (always current)

**Daily Snapshots:**
- 10.5281/zenodo.17987676 — AUTO-DZ-ACT-3I-ATLAS-DAILY

**Related Scientific Supplements:**
- 10.5281/zenodo.15327005 — STOE vs GR
- 10.5281/zenodo.16211838 — MRI–Gravity logic

### Execution (Offline-First)

```bash
# Offline mode (recommended)
python src/ingest/ingest_entrypoint.py \
  --source zenodo \
  --doi 10.5281/zenodo.16292189 \
  --mode ingest \
  --input /path/to/offline/zenodo_record.json

# Online mode (requires network)
python src/ingest/ingest_entrypoint.py \
  --source zenodo \
  --doi 10.5281/zenodo.16292189 \
  --mode ingest

# Dry-run mode (validation only)
python src/ingest/ingest_entrypoint.py \
  --source zenodo \
  --doi 10.5281/zenodo.16292189 \
  --mode ingest \
  --input /path/to/file.json \
  --output-only
```

### Output Structure

```
data/raw/<YYYY-MM-DD>/zenodo_<DOI_SUFFIX>/
  records/<record_id>.json
  payload/<record_id>__payload.json
```

Example for DOI `10.5281/zenodo.16292189`:
```
data/raw/2025-12-21/zenodo_16292189/
  records/835c6754-0679-4fbc-b8e0-21378ff4b840.json
  payload/835c6754-0679-4fbc-b8e0-21378ff4b840__payload.json
```

### Success Criteria

A successful Zenodo ingest produces:

1. **Record file** (`records/<record_id>.json`) containing:
   - `record_id` (UUID v4)
   - `retrieved_utc` (timezone-aware UTC ISO-8601)
   - `provenance` with `source`, `doi`, `version`
   - `sha256` (computed from payload bytes on disk)
   - `size_bytes` (actual payload size)

2. **Payload file** (`payload/<record_id>__payload.json`) containing:
   - Complete Zenodo record data as retrieved

3. **Integrity verification**:
   - SHA256 hash matches payload bytes
   - Size matches actual file size
   - No overwrites (collision-safe record IDs)

### Error Handling

All errors emit structured output:
```
[ERROR] <description>
[HINT] <actionable guidance>
[HINT] <additional guidance if applicable>
```

Exit codes:
- `0` = Success
- Non-zero = Failure (see error messages)

---

## General Ingest Rules

### Immutability

1. **Never overwrite**: If a record_id collision occurs, regenerate UUID
2. **Append-only**: Existing records are never modified
3. **Deterministic paths**: Directory structure based on date and source

### Offline-First

1. **--input takes precedence**: Always use offline file when provided
2. **Network optional**: Online fetch is a convenience, not a requirement
3. **Graceful degradation**: Network failures produce helpful error messages

### Audit Trail

All RAW records include:
- Timezone-aware UTC timestamps
- Complete provenance metadata
- Cryptographic integrity checks (SHA-256)
- Immutable record IDs (UUID v4)

---

## End of Document
