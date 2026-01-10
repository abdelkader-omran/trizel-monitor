# TRIZEL Monitor

**TRIZEL Monitor** is an automated scientific monitoring system designed to track, collect, and archive all *officially published data* related to the interstellar object **3I/ATLAS**.

The project is built to operate with **zero daily manual intervention**, relying on GitHub Actions to execute scheduled and on-demand monitoring workflows.

---

## Objectives

- Continuous monitoring of official datasets released by:
  - NASA / JPL
  - ESA
  - CNSA
  - JAXA
  - MPC and other recognized international institutions
- Centralized archival of observation timestamps and update signals
- Strict attribution to original official sources
- Reproducible and auditable automation logic (AUTO DZ ACT framework)

---

## Automation

The repository includes a GitHub Actions workflow:

- **Daily Official Data Monitor**
  - Manual trigger (`workflow_dispatch`)
  - Scheduled execution (UTC-based)
  - Python-based monitoring logic
  - Automatic logging of execution timestamps

All automation is executed inside GitHub infrastructure.  
No local machine or external server is required.

---

## Scientific Integrity

This repository does **not** modify, reinterpret, or alter official datasets.  
Its role is limited to **monitoring, indexing, and traceability**.

All analyses derived from this system must explicitly reference original sources.

---

## Status

- Automation: **Active**
- Last execution: recorded automatically
- Maintenance: not required for daily operation

---

## Raw Data Policy

**TRIZEL Monitor** enforces strict data classification and archival integrity rules to ensure scientific reproducibility and transparency.

### Data Classification System

All data produced by this system is explicitly classified into one of three mutually exclusive categories:

1. **RAW_DATA** — Official agency source data
   - Direct from verified space agency endpoints
   - Independently downloadable and verifiable
   - Traceable to official source with retrieval timestamp
   - Includes checksum for integrity verification
   - **Label:** `RAW DATA — OFFICIAL AGENCY SOURCE`
   - **Visual:** Green badge ✓ RAW

2. **SNAPSHOT** — Derivative/computed data
   - API responses containing processed information
   - Computed orbital elements or aggregated data
   - **Warning:** Snapshots have zero scientific value alone
   - Must reference original RAW_DATA source
   - **Label:** `SNAPSHOT — DERIVATIVE DATA`
   - **Visual:** Orange badge ⚠ SNAPSHOT

3. **DERIVED** — Computed/analyzed data
   - Results from scientific computation or analysis
   - Must cite input data sources
   - **Label:** `DERIVED — COMPUTED DATA`
   - **Visual:** Blue badge → DERIVED

### Mandatory Metadata

Every data file contains the following mandatory fields:

- `data_class`: Explicit classification (RAW_DATA | SNAPSHOT | DERIVED)
- `source_agency`: Trusted agency (NASA, ESA, CNSA, Roscosmos, JAXA, MPC)
- `agency_endpoint`: Official endpoint URL
- `license`: Data license information
- `delay_policy`: Real-time vs delayed release assumptions
- `checksum`: SHA256 integrity hash
- `retrieval_timestamp`: ISO-8601 UTC timestamp
- `visual_attributes`: UI rendering metadata (label, color, badge, icon)

### Trusted Agency Whitelist

Only data from the following agencies may be classified as RAW_DATA:

- **NASA** (National Aeronautics and Space Administration, USA)
- **ESA** (European Space Agency, Europe)
- **CNSA** (China National Space Administration, China)
- **Roscosmos** (Roscosmos State Corporation, Russia)
- **JAXA** (Japan Aerospace Exploration Agency, Japan)
- **MPC** (Minor Planet Center, IAU)

### Scientific Rule

**A dataset has scientific value ONLY if it is explicitly identified as RAW DATA, traceable to an official space agency source, independently downloadable, and verifiable.**

Snapshots without linked raw data are archival artifacts, not scientific evidence.

### Default Assumptions

- **NO real-time raw data by default** (`raw_release_delay: true`)
- Real-time claims require explicit agency documentation
- If raw data is unavailable → `data_class: SNAPSHOT` + warning

### Validation

All data files are automatically validated against the schema:
- CI/CD checks enforce mandatory fields
- Schema validation prevents incomplete metadata
- Checksums ensure data integrity
- Missing fields cause build failures

### Agency Endpoints

The system maintains a registry of verified agency endpoints. See `src/data_classification.py` for the complete list.

Current integrated endpoints:
- NASA JPL SBDB API (snapshot data)
- NASA JPL Horizons API (computed ephemerides)
- NASA PDS (raw mission data)
- ESA Science Archives (raw observations)
- JAXA DARTS (mission archives)
- MPC Database (astrometry)

---

## License

This project is provided for scientific monitoring and research transparency purposes.
