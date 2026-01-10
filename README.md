# TRIZEL Monitor

**Version:** 3.0.0  
**Data Governance:** v3.0.0

**TRIZEL Monitor** is an automated scientific monitoring system designed to track, collect, and archive data related to the interstellar object **3I/ATLAS**.

The project is built to operate with **zero daily manual intervention**, relying on GitHub Actions to execute scheduled and on-demand monitoring workflows.

**See:** [CHANGELOG.md](CHANGELOG.md) for version history and [DATA_CONTRACT.md](DATA_CONTRACT.md) for authoritative data contract.

---

## Backward Compatibility Notice

**Versions < 3.0.0** may contain snapshot data without explicit RAW_DATA guarantees.

For scientific reproducibility and verifiable raw data provenance, **use v3.0.0 or later**.

---

## Objectives

- Continuous monitoring of official datasets from authorized agencies:
  - **NASA** (National Aeronautics and Space Administration)
  - **ESA** (European Space Agency)
  - **JAXA** (Japan Aerospace Exploration Agency)
  - **CNSA** (China National Space Administration) - Monitoring status
  - **ROSCOSMOS** (Russian Federal Space Agency) - Monitoring status
  - **MPC** (Minor Planet Center - IAU)
- RAW data download capability from agencies with public archives
- Strict data classification (RAW_DATA, SNAPSHOT, DERIVED)
- SHA-256 checksums for all data files (MD5 forbidden)
- Centralized archival of observation timestamps and update signals
- Strict attribution to original official sources
- Reproducible and auditable automation logic

---

## Data Classification

All data is classified according to strict scientific rules:

| Classification | Description | Visual | Example |
|----------------|-------------|--------|---------|
| **RAW_DATA** | Original archival files from official agencies (direct download only) | 🟢 ✓ RAW DATA | FITS files, original telemetry |
| **SNAPSHOT** | API responses, computed values, real-time queries | 🟠 ⚠ SNAPSHOT – NO SCIENTIFIC VALUE ALONE | JPL SBDB API responses |
| **DERIVED** | Processed, analyzed, or transformed data | 🔵 → DERIVED DATA | Analysis results, visualizations |

**IMPORTANT:** API responses (like JPL SBDB) are classified as **SNAPSHOT**, not RAW_DATA, because they contain computed orbital elements, not original archival files.

---

## Data Structure

All data files follow a strict schema with **exactly ONE metadata block**:

```json
{
  "trizel_metadata": {
    "project": "TRIZEL Monitor",
    "data_classification": "SNAPSHOT | RAW_DATA | DERIVED",
    "source_agency": "NASA | ESA | JAXA | MPC",
    "checksum": {
      "algorithm": "sha256",
      "value": "..."
    },
    "visual_attributes": {...},
    ...
  },
  "data": {...}
}
```

See [DATA_CONTRACT.md](DATA_CONTRACT.md) for complete schema specification.

---

## File Inventory

Current data files (as of 2026-01-10):

- **snapshot_3I_ATLAS_latest.json** - Latest SNAPSHOT from JPL SBDB API
- **snapshot_3I_ATLAS_YYYYMMDD_HHMMSS.json** - Timestamped SNAPSHOT files

All files are validated against the authoritative data contract.

---

## Automation

The repository includes GitHub Actions workflows:

- **Daily Official Data Monitor** (`daily.yml`)
  - Manual trigger (`workflow_dispatch`)
  - Scheduled execution (UTC-based)
  - Python-based monitoring logic
  - Automatic logging of execution timestamps
  - Generates SNAPSHOT data files from JPL SBDB API

- **Data Governance Validation** (`validation.yml`)
  - Validates all data files against authoritative contract
  - Enforces single metadata block rule
  - Validates data classification rules
  - Checks checksum policy (SHA-256 only, MD5 forbidden)
  - Runs on every push and pull request

All automation is executed inside GitHub infrastructure.  
No local machine or external server is required.

---

## Scientific Integrity

This repository does **not** modify, reinterpret, or alter official datasets.  
Its role is limited to **monitoring, indexing, and traceability**.

**Key Principles:**
- All data correctly classified (SNAPSHOT for API data, RAW_DATA for archival downloads)
- SHA-256 checksums ensure data integrity
- Visual attributes provide clear semantic meaning
- No MD5 usage (cryptographically broken, forbidden)

All analyses derived from this system must explicitly reference original sources.

---

## Validation

Data files are validated against strict rules:

1. **Single metadata block:** `trizel_metadata` only at root level
2. **No duplicates:** No nested or duplicated metadata blocks
3. **RAW_DATA rules:** Only for direct archival downloads from official agencies
4. **Agency whitelist:** Only NASA, ESA, JAXA, MPC allowed
5. **Checksum policy:** SHA-256 required, MD5 forbidden
6. **Visual attributes:** Must match classification

Run validation manually:
```bash
python src/validate_data.py
```

---

## Status

- Automation: **Active**
- Data Governance: **v2.0.0**
- Validation: **Enforced via CI**
- Last execution: recorded automatically
- Maintenance: not required for daily operation

---

## Documentation

- **[DATA_CONTRACT.md](DATA_CONTRACT.md)** - Authoritative data contract and schema specification
- **[AUTHORITATIVE_RAW_DATA_GOVERNANCE.md](docs/governance/AUTHORITATIVE_RAW_DATA_GOVERNANCE.md)** - Complete RAW data and agency connectivity governance
- **[AGENCY_CONNECTIVITY_STATUS.md](docs/status/AGENCY_CONNECTIVITY_STATUS.md)** - Current agency connectivity status
- **[ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md](ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md)** - Historical governance framework

---

## Communication Policy

**IMPORTANT:** TRIZEL-AI does not provide direct messaging.

All communication is conducted through **verifiable channels only:**
- **GitHub** (issues, pull requests, discussions)
- **ORCID** (research profiles)
- **DOI-linked archival records** (Zenodo, OSF, HAL)

No other communication channels are authorized.

---

## License

This project is provided for scientific monitoring and research transparency purposes.
