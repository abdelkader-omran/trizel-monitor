# CHANGELOG

All notable changes to TRIZEL Monitor are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2026-01-10

### BREAKING CHANGES
- Strict RAW_DATA vs SNAPSHOT classification enforcement
- New mandatory metadata schema with single `trizel_metadata` block
- SHA-256 checksums required for all data files (MD5 forbidden)
- Visual attributes required for all data classifications

### Added - Agency Connectivity
- International agency registry (`config/agency_registry.json`)
- NASA (National Aeronautics and Space Administration) - Active
- ESA (European Space Agency) - Active
- JAXA (Japan Aerospace Exploration Agency) - Active
- CNSA (China National Space Administration) - Monitoring status
- ROSCOSMOS (Russian Federal Space Agency) - Monitoring status
- MPC (Minor Planet Center) - Active
- Agency status semantics: Active/Monitoring/Limited

### Added - RAW Data Infrastructure
- RAW data download system (`src/raw_download/`)
- Direct file download with SHA-256 verification
- Polite rate limiting and retry logic
- Storage structure: `data/raw/<agency_id>/<dataset_id>/`
- Sidecar metadata (`.meta.json`) for all RAW files
- Provenance tracking (source_url, license, delay_policy)

### Added - Governance Framework
- Authoritative governance document (`docs/governance/AUTHORITATIVE_RAW_DATA_GOVERNANCE.md`)
- Supersession notice for previous partial implementations
- Strict RAW_DATA requirements (6 mandatory conditions)
- Visual differentiation system (Green/Orange/Blue for RAW/SNAPSHOT/DERIVED)
- Communication policy enforcement (GitHub/ORCID/DOI only)

### Added - Automation & Validation
- Agency connectivity audit generator (`scripts/generate_audit.py`)
- Agency connectivity status generator (`scripts/generate_status.py`)
- Complete system validator (`scripts/validate_system.py`)
- Build metadata generator (`scripts/generate_build_metadata.py`)
- ATLAS snapshot ingest bridge (`scripts/ingest_atlas_snapshots.py`)
- Automated audit report (`docs/audit/AGENCY_CONNECTIVITY_AUDIT.json`)
- Automated status document (`docs/status/AGENCY_CONNECTIVITY_STATUS.md`)

### Added - Researcher UI
- Public-facing research portal (`site/`)
- Home page with system overview
- Status page with operational metrics
- Agency registry viewer
- RAW data catalog (verifiable downloads only)
- Snapshot catalog (with explicit warnings)
- Policy and governance viewer
- Human-readable sitemap
- Accessible, responsive design
- Reduced-motion compatible
- Communication policy footer on all pages

### Added - Configuration Management
- Zenodo DOI configuration (`config/zenodo_config.json`)
- Non-hardcoded DOI references
- ATLAS daily repository integration support

### Changed - Data Contract
- Data governance version: 2.0.0 → 3.0.0 alignment
- Updated agency whitelist (added CNSA, ROSCOSMOS)
- Enhanced validation rules for RAW_DATA classification
- CI enforcement of all governance rules

### Changed - Validation
- Extended agency whitelist in `src/validate_data.py`
- Extended agency constants in `src/main.py`
- Added system-wide validation (`scripts/validate_system.py`)
- CI workflow enhanced with audit/status generation

### Changed - Documentation
- Updated README.md with agency list and communication policy
- Updated agency references throughout documentation
- Added backward compatibility notice

### Security
- Enforced SHA-256 checksums (MD5 forbidden)
- CI fails on any MD5 usage
- Provenance tracking for all RAW data
- Verification methods documented for each endpoint

### Notes
- CNSA and ROSCOSMOS marked as "Monitoring" (accurate reflection of limited public raw data access)
- RAW_DATA classification requires verifiable proof of public downloadability
- SNAPSHOT classification used for API responses and computed values (e.g., JPL SBDB)
- Zero interpretation policy enforced throughout UI and documentation

---

## [2.0.0] - 2026-01-10 (Historical)

### Added
- Single metadata block enforcement (`trizel_metadata`)
- Data classification system (RAW_DATA, SNAPSHOT, DERIVED)
- SHA-256 checksum policy
- Visual attributes for data types
- Authoritative data contract (DATA_CONTRACT.md)

### Changed
- Migrated from multiple metadata blocks to single `trizel_metadata` block
- Replaced MD5 with SHA-256 checksums
- Enhanced validation with strict classification rules

### Removed
- Legacy metadata structures (`metadata`, `sbdb_data`, `sbdb_error` at root)
- MD5 checksum support (forbidden)

---

## [1.0.0] - Earlier (Historical)

### Added
- Initial automated monitoring system
- JPL SBDB API integration
- GitHub Actions workflows
- Basic data validation

---

## Backward Compatibility Notice

**Versions < 3.0.0** may contain snapshot data without explicit RAW_DATA guarantees.

For scientific reproducibility and verifiable raw data provenance, **use v3.0.0 or later**.

Migration from v2.x to v3.0.0:
- Existing data files remain valid (backward compatible)
- New RAW_DATA requirements apply to new data only
- Agency registry now authoritative source of truth
- UI provides verification interface for researchers
