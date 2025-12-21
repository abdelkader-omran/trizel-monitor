# TRIZEL Monitor - Tools

This directory contains baseline acquisition tools for the TRIZEL Monitor project.

## Overview

The tools in this directory support scientific data ingestion following principles of:
- **Immutability**: RAW records are never modified after writing
- **Provenance**: Each record includes complete source metadata
- **Deterministic Layout**: Records organized by date, source, and dataset

## Tools

### `fetch_horizons.py`

Baseline acquisition tool for NASA JPL Horizons API data.

**Purpose**: Fetch ephemerides data from NASA JPL Horizons system and write RAW records to deterministic layout.

**Usage**:

```bash
# Offline mode (recommended for reproducibility)
python tools/fetch_horizons.py --input data/official_snapshot_latest.json

# Online mode (fetch from API)
python tools/fetch_horizons.py --target "3I/ATLAS"

# Dry-run mode (test output structure)
python tools/fetch_horizons.py --output-only
```

**Output Structure**:

Records are written to: `data/raw/<YYYY-MM-DD>/<SOURCE_ID>/<DATASET_KEY>/`

Example:
```
data/raw/2025-12-21/NASA_JPL_HORIZONS/horizons_api/
├── payload/
│   └── <record_id>__payload.json
└── records/
    └── <record_id>.json
```

**Record Format**:

Each record includes:
- `record_id`: Unique UUID for this record
- `source`: Source identifier (e.g., "NASA_JPL_HORIZONS")
- `dataset`: Dataset key (e.g., "horizons_api")
- `target`: Target object designation
- `retrieved_utc`: Timestamp of retrieval
- `date`: Date of ingestion (YYYY-MM-DD)
- `offline_mode`: Whether this was offline ingestion
- `payload_path`: Relative path to payload file
- `api_url`: API endpoint (null for offline mode)

**Error Handling**:

The tool provides actionable error messages:
- Missing input file → recommends checking file path or using online mode
- Network errors → recommends offline mode with cached data
- API errors → provides details and suggests troubleshooting steps

## Integration with Main Orchestration

The tools are invoked via the main entry point (`src/main.py`) using `--mode ingest`:

```bash
# Use ingest mode with offline input
python src/main.py --mode ingest --input data/official_snapshot_latest.json

# Use ingest mode (auto-detects offline input)
python src/main.py --mode ingest
```

## Scientific Integrity

All tools in this directory adhere to the TRIZEL Monitor data contract:
1. **No modification**: Source data is preserved verbatim
2. **Complete provenance**: Every record traces back to its source
3. **Reproducibility**: Same input produces same output structure
4. **Auditability**: All operations are logged and traceable

See `DATA_CONTRACT.md` for the full specification.
