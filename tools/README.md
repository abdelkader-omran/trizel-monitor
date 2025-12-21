# JPL Horizons Data Acquisition System

## Overview

This directory contains the complete data acquisition infrastructure for fetching data from NASA/JPL Horizons API for the 3I/ATLAS object.

## Components

### 1. Schema Definition
- **`spec/raw_record.schema.json`**: JSON Schema v7 defining the structure of raw data records

### 2. Data Source Registry
- **`data/metadata/sources.json`**: Registry of official data sources with endpoint definitions

### 3. Tools

#### `tools/fetch_horizons.py`
Main data acquisition tool that:
- Fetches data from JPL Horizons API (or uses local file for reproducibility)
- Saves raw response to `data/raw/JPL_HORIZONS/<YYYY-MM-DD>/horizons_<query_id>.json`
- Generates schema-compliant record in `data/records/`
- Computes SHA-256 hash for integrity verification
- Records UTC timestamps in ISO-8601 format

**Usage:**
```bash
# Fetch from API (requires network access to ssd.jpl.nasa.gov)
python3 tools/fetch_horizons.py

# Use local file for reproducibility (when API is blocked)
python3 tools/fetch_horizons.py --input horizons_response.json

# Custom query ID for filename
python3 tools/fetch_horizons.py --query-id custom_id
```

#### `tools/validate_raw_record.py`
Validation tool that verifies:
- Schema compliance (against `spec/raw_record.schema.json`)
- Source registry compliance (against `data/metadata/sources.json`)
- Raw data file existence and SHA-256 hash integrity

**Usage:**
```bash
python3 tools/validate_raw_record.py data/records/JPL_HORIZONS__horizons_api.sample.json
```

## Data Flow

1. **Acquisition**: `fetch_horizons.py` retrieves data from Horizons API
2. **Storage**: Raw response saved to timestamped directory
3. **Record Creation**: Schema-compliant JSON record generated
4. **Validation**: `validate_raw_record.py` verifies all constraints

## Directory Structure

```
.
├── spec/
│   └── raw_record.schema.json          # Record schema
├── data/
│   ├── metadata/
│   │   └── sources.json                # Source registry
│   ├── raw/
│   │   └── JPL_HORIZONS/
│   │       └── <YYYY-MM-DD>/
│   │           └── horizons_*.json     # Raw responses
│   └── records/
│       └── JPL_HORIZONS__*.json        # Schema-compliant records
└── tools/
    ├── fetch_horizons.py               # Acquisition tool
    └── validate_raw_record.py          # Validation tool
```

## Reproducibility

The system is designed for full reproducibility:

1. **Deterministic parameters**: Fixed query parameters for 3I/ATLAS
2. **Timestamped storage**: Raw data organized by date
3. **Hash verification**: SHA-256 ensures data integrity
4. **Offline operation**: `--input` option allows using saved responses

Same input → Same output (except timestamps)

## Validation Example

After running `fetch_horizons.py`, validate the record:

```bash
$ python3 tools/validate_raw_record.py data/records/JPL_HORIZONS__horizons_api.sample.json

Validating: data/records/JPL_HORIZONS__horizons_api.sample.json
Schema: /path/to/spec/raw_record.schema.json
Sources: /path/to/data/metadata/sources.json

1. Validating against schema...
  ✓ Schema validation passed

2. Validating against sources registry...
  ✓ Sources validation passed

3. Validating raw data file...
  ✓ Raw data file validation passed

✓ ALL VALIDATIONS PASSED
```

## Requirements

- Python 3.7+
- `requests` library: `pip install requests`

## Hard Rules

As specified in the problem statement:

- ✅ No interpretation of scientific content (raw storage only)
- ✅ Deterministic request parameters
- ✅ SHA-256 computed and stored
- ✅ UTC timestamps in ISO-8601
- ✅ Schema compliance validated
- ✅ source_id = "JPL_HORIZONS", endpoint_id = "horizons_api"
- ✅ Offline mode with `--input` option
- ✅ No new schemas or sources unless explicitly requested
