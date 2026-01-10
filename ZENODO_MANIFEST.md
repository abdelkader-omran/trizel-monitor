# ZENODO ARCHIVAL MANIFEST

## Repository Information

- **Repository:** abdelkader-omran/trizel-monitor
- **Branch:** main
- **Purpose:** Source-level data ingestion & raw-data archival authority for 3I-ATLAS program
- **Role:** TRIZEL / AUTO-DZ-ACT / 3I-ATLAS program data foundation

---

## Archive Classification

This repository contains scientifically classified data artifacts organized for long-term archival.

### Data Classes

1. **RAW_DATA** — Original, unmodified data from official international space agencies
2. **SNAPSHOT** — Timestamped system state captures and aggregations
3. **DERIVED** — Processed, computed, or synthesized data products

---

## Current Archive Statistics

**Total Data Files:** 17  
**RAW_DATA:** 7 files  
**SNAPSHOT:** 6 files  
**DERIVED:** 4 files

**Source Agencies:**
- NASA: 7 RAW_DATA files
- INTERNAL: 10 SNAPSHOT/DERIVED files

---

## RAW DATA Archives

### NASA/JPL Small-Body Database (SBDB) Records

**Source:** NASA/JPL Small-Body Database API  
**Endpoint:** https://ssd-api.jpl.nasa.gov/sbdb.api  
**License:** CC0-1.0 (Public Domain - NASA Open Data Policy)  
**Verification Status:** VERIFIED

**Files:**
1. `jpl_sbdb_20251218_191351.json` — Retrieved: 2025-12-18T19:13:51Z
2. `jpl_sbdb_20251218_192722.json` — Retrieved: 2025-12-18T19:27:22Z
3. `jpl_sbdb_20251218_192757.json` — Retrieved: 2025-12-18T19:27:57Z
4. `jpl_sbdb_20251218_192932.json` — Retrieved: 2025-12-18T19:29:32Z
5. `jpl_sbdb_20251218_192942.json` — Retrieved: 2025-12-18T19:29:42Z
6. `jpl_sbdb_20251218_201107.json` — Retrieved: 2025-12-18T20:11:07Z
7. `jpl_sbdb_20251218_202539.json` — Retrieved: 2025-12-18T20:25:39Z

**Metadata Guarantees:**
- Unmodified agency data
- Cryptographic checksums (SHA-256)
- Independently verifiable
- Direct API traceability

---

## SNAPSHOT Collections

**Purpose:** Timestamped captures of system state aggregating raw data sources  
**Source Agency:** INTERNAL (TRIZEL Monitor pipeline)  
**License:** CC-BY-4.0 (Attribution required)

**Raw Data Linkage:**  
All snapshots reference NASA/JPL SBDB raw data files as primary sources.

**Files:**
1. `official_snapshot_3I_ATLAS_20251219_091518.json`
2. `official_snapshot_3I_ATLAS_20251219_105036.json`
3. `official_snapshot_3I_ATLAS_20251220_033140.json`
4. `official_snapshot_3I_ATLAS_20251221_034514.json`
5. `official_snapshot_latest.json` (rolling latest)
6. `latest_jpl_sbdb.json` (rolling latest)

**Scientific Limitation:**  
Snapshots are archival records, not primary scientific evidence. All scientific claims must trace to RAW_DATA sources.

---

## DERIVED Datasets

**Purpose:** Structured registries and processed data products  
**Processing Pipeline:** TRIZEL Monitor v1.0  
**License:** CC-BY-4.0

**Files:**
1. `platforms_registry_20251219_091518.json`
2. `platforms_registry_20251219_105036.json`
3. `platforms_registry_20251220_033140.json`
4. `platforms_registry_20251221_034514.json`

**Content:**  
Registry of official space agencies, observatories, and data platforms relevant to 3I/ATLAS monitoring.

---

## Verification and Integrity

### Checksums

All files include SHA-256 checksums in metadata.  
Independent verification: See `data/DATA_MANIFEST.json`

### Metadata Schema

All files comply with TRIZEL Monitor Metadata Schema v1.0.0  
Specification: `METADATA_SCHEMA.md`

### Validation

- Automated CI validation enforces metadata compliance
- 100% of files are classified and verified
- No manual overrides permitted

---

## Zenodo Release Guidelines

### Version Organization

Each Zenodo version should:
1. Include complete `DATA_MANIFEST.json`
2. Preserve all file classifications
3. Maintain checksum integrity
4. Reference this archival manifest

### DOI Continuity

- Do NOT delete previous versions
- Use Zenodo's versioning mechanism
- Preserve metadata across versions
- Link to predecessor DOIs

### Recommended Archive Structure

```
zenodo-release-vX.Y.Z/
├── RAW_DATA/
│   ├── jpl_sbdb_*.json (NASA/JPL data)
│   └── README_RAW_DATA.txt
├── SNAPSHOT/
│   ├── official_snapshot_*.json
│   └── README_SNAPSHOT.txt
├── DERIVED/
│   ├── platforms_registry_*.json
│   └── README_DERIVED.txt
├── DATA_MANIFEST.json
├── METADATA_SCHEMA.md
└── ZENODO_MANIFEST.md (this file)
```

### Required Metadata in Zenodo Record

**Title:** TRIZEL Monitor — 3I/ATLAS Data Archive vX.Y.Z

**Description:**  
Scientific data archive for interstellar object 3I/ATLAS monitoring. Includes RAW_DATA from NASA/JPL, timestamped SNAPSHOTs, and DERIVED platform registries. All data classified, verified, and traceable to official international space agencies.

**Keywords:**
- 3I/ATLAS
- Interstellar Objects
- NASA JPL
- Small-Body Database
- Orbital Elements
- Raw Data Archive
- Scientific Provenance

**License:**  
Mixed (see file-level metadata):
- RAW_DATA: CC0-1.0 (Public Domain)
- SNAPSHOT/DERIVED: CC-BY-4.0

**Related Identifiers:**
- Repository: https://github.com/abdelkader-omran/trizel-monitor
- Previous version DOI: (if applicable)
- NASA SBDB API: https://ssd-api.jpl.nasa.gov/

---

## Scientific Integrity Statement

This archive maintains strict separation between:
1. **Raw data** from official space agencies (independently verifiable)
2. **Snapshots** (timestamped aggregations, traceable to raw sources)
3. **Derived data** (processed products with documented pipelines)

**All scientific claims must be traceable to RAW_DATA sources.**

Snapshots without raw data linkage are archival records, not scientific evidence.

---

## Downstream Usage

### Permitted Uses

- Read-only access to classified data
- Citation of RAW_DATA sources
- Temporal analysis using SNAPSHOTs
- Building on DERIVED registries

### Prohibited Actions

- Reclassifying RAW_DATA as SNAPSHOT or DERIVED
- Modifying metadata fields
- Breaking provenance chain
- Claiming snapshot data as raw data

---

## Archive Authority

**Maintained by:** TRIZEL Monitor Project  
**Scientific Standard:** TRIZEL / AUTO-DZ-ACT / 3I-ATLAS program  
**Last Updated:** 2026-01-10  
**Schema Version:** 1.0.0

---

## Contact and Issues

- **Repository:** https://github.com/abdelkader-omran/trizel-monitor
- **Issues:** Use GitHub Issues for questions or corrections
- **Data Integrity:** All modifications logged via Git history

---

## End of Manifest

This manifest is version-controlled and updated with each archival release.
