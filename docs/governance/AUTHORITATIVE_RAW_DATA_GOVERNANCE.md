# AUTHORITATIVE RAW DATA GOVERNANCE

**Version:** 1.0.0  
**Status:** AUTHORITATIVE  
**Last Updated:** 2026-01-10  
**Supersedes:** All previous partial governance documents

---

## 1. PURPOSE AND SCOPE

This document defines the **complete and authoritative governance framework** for the TRIZEL Monitor raw data archive and agency connectivity system.

### 1.1 Primary Objectives

1. **Ensure the archive is a genuine RAW_DATA archive** (downloadable agency datasets) and not merely a collection of snapshots
2. **Ensure actual connectivity to international space agencies** with ability to download RAW_DATA when permitted
3. **Clearly flag limited/monitor-only sources** where raw data download is not publicly available

### 1.2 Non-Negotiable Principles

- **No interpretation, no narrative, no scientific claims**
- **Evidence-first:** Pointers + verifiable provenance only
- **RAW_DATA allowed ONLY when:**
  - (a) Directly downloadable file
  - (b) Official agency endpoint
  - (c) License/policy indicated
  - (d) Checksum computed
  - (e) Delay policy stated
- **SNAPSHOT/DERIVED explicitly labeled** and visually differentiated
- **SNAPSHOT alone has no scientific value** for raw-data analysis

---

## 2. AGENCY REGISTRY (SINGLE SOURCE OF TRUTH)

### 2.1 Authoritative Registry

**Location:** `config/agency_registry.json`

This is the **ONLY** authoritative source for:
- Agency definitions
- Endpoint configurations
- Data access capabilities
- Status classifications

### 2.2 Required Agencies

The following agencies **MUST** be explicitly present:

| Agency ID | Name | Required | Status |
|-----------|------|----------|---------|
| NASA | National Aeronautics and Space Administration | ✓ | Active |
| ESA | European Space Agency | ✓ | Active |
| JAXA | Japan Aerospace Exploration Agency | ✓ | Active |
| CNSA | China National Space Administration | ✓ | Monitoring |
| ROSCOSMOS | Russian Federal Space Agency | ✓ | Monitoring |
| MPC | Minor Planet Center (IAU) | ✓ | Active |

### 2.3 Agency Status Semantics

**Active:**
- Publicly downloadable RAW datasets exist
- Download implementation exists in codebase
- No credentials required for access

**Monitoring:**
- Agency exists but raw download not implemented
- OR not publicly accessible without credentials
- System monitors official channels for updates

**Limited:**
- Only catalogs/metadata available without authentication
- OR only derived products publicly accessible

### 2.4 Endpoint Requirements

Each endpoint entry **MUST** include:

```json
{
  "endpoint_id": "unique_identifier",
  "url": "https://...",
  "data_type": "RAW_DATA | SNAPSHOT | DERIVED | CATALOG",
  "requires_auth": true/false,
  "license_or_policy_ref": "URL or description",
  "delay_policy_default": "Description of data release timing",
  "download_mode": "DIRECT_FILE | API_JSON | HTML_INDEX | AUTH_REQUIRED",
  "verification_method": "CHECKSUM | SIGNATURE | NONE"
}
```

---

## 3. DATA CLASSIFICATION RULES

### 3.1 Three-Tier Classification System

**RAW_DATA** 🟢 ✓
- Original archival files from official agencies
- Direct downloads only (not API responses)
- Examples: FITS files, observation data, telemetry

**SNAPSHOT** 🟠 ⚠
- API responses
- Computed orbital elements
- Real-time queries
- **Explicit warning:** "NO SCIENTIFIC VALUE ALONE"

**DERIVED** 🔵 →
- Processed data
- Analysis results
- Computed metrics

### 3.2 RAW_DATA Requirements (STRICT)

Data **MAY ONLY** be classified as RAW_DATA if **ALL** conditions are met:

1. ✓ Source is official agency (NASA, ESA, JAXA, MPC, or approved agency)
2. ✓ Direct download from archival system (not API summary)
3. ✓ Explicit provenance documented (source URL, checksum, policy)
4. ✓ SHA-256 checksum computed and verified
5. ✓ License or policy reference included
6. ✓ Delay policy statement included

### 3.3 Classification Enforcement

**CI MUST FAIL if:**
- RAW_DATA claimed without meeting all requirements
- API response classified as RAW_DATA
- Missing checksum for RAW_DATA
- MD5 used instead of SHA-256
- Legacy metadata blocks present

---

## 4. RAW DATA DOWNLOAD SYSTEM

### 4.1 Download Subsystem Location

**Path:** `src/raw_download/`

### 4.2 Required Capabilities

The download system **MUST** support:

1. **DIRECT_FILE downloads** with content-length verification
2. **SHA-256 checksum** computation and storage
3. **Polite rate limits** (minimum 2 seconds between requests)
4. **Retry logic** for transient failures
5. **Storage structure:** `data/raw/<agency_id>/<dataset_id>/`

### 4.3 Sidecar Metadata

Every downloaded RAW file **MUST** have a sidecar metadata file:

**Naming:** `<filename>.meta.json`

**Required structure:**
```json
{
  "trizel_metadata": {
    "project": "TRIZEL Monitor",
    "data_classification": "RAW_DATA",
    "source_agency": "NASA|ESA|JAXA|MPC",
    "checksum_sha256": "hex_string",
    "retrieval_timestamp_utc": "ISO-8601",
    "source_url": "https://...",
    "license_or_policy_ref": "...",
    "delay_policy": "...",
    "visual_attributes": {
      "color": "green",
      "icon": "✓",
      "label": "RAW DATA"
    }
  }
}
```

### 4.4 Implementation Status

**Minimum requirement:** At least ONE working sample dataset downloader for agencies where public raw data exists.

**Current status:**
- NASA: Framework implemented (placeholder for PDS access)
- ESA: Framework implemented (placeholder for ESA Archives)
- JAXA: Framework implemented (placeholder for DARTS access)
- MPC: Framework implemented (placeholder for observation database)
- CNSA: Monitoring only (no public raw download without credentials)
- ROSCOSMOS: Monitoring only (no public raw download without credentials)

**Note:** CNSA and ROSCOSMOS are correctly marked as "Monitoring" because publicly accessible raw data downloads are not available without institutional credentials. This is **NOT** a limitation of the system but an accurate reflection of these agencies' data policies.

---

## 5. VISUAL DIFFERENTIATION

### 5.1 Visual Attributes (MANDATORY)

Every data file and endpoint **MUST** include visual attributes:

| Classification | Color | Icon | Label |
|----------------|-------|------|-------|
| RAW_DATA | Green (🟢) | ✓ | RAW DATA |
| SNAPSHOT | Orange (🟠) | ⚠ | SNAPSHOT – NO SCIENTIFIC VALUE ALONE |
| DERIVED | Blue (🔵) | → | DERIVED DATA |

### 5.2 User Clarity Requirement

It **MUST** be impossible for a user or researcher to:
- Confuse SNAPSHOT with RAW_DATA
- Mistake computed values for archival observations
- Misinterpret data classification

This is enforced through:
- Color coding
- Explicit warning labels
- CI validation
- Documentation

---

## 6. ATLAS PIPELINE INTEGRATION

### 6.1 Daily Snapshot Repository Integration

**Target repository:** `abdelkader-omran/AUTO-DZ-ACT-3I-ATLAS-DAILY`

### 6.2 Classification Rules for Daily Snapshots

Daily snapshots from the ATLAS pipeline **MUST** be classified as:
- **SNAPSHOT** if they contain API responses or computed values
- **RAW_DATA** only if they contain verified downloadable agency datasets

**Default:** SNAPSHOT (unless explicitly verified as RAW_DATA)

### 6.3 Zenodo DOI Management

Zenodo DOI references **MUST NOT** be hardcoded. Instead:
- Store as `latest_release_doi` in configuration
- Update programmatically when new releases are published
- Include in sidecar metadata for archival records

---

## 7. VALIDATION AND ENFORCEMENT

### 7.1 Automated Validation

**Script:** `src/validate_data.py`

**CI Integration:** `.github/workflows/validation.yml`

### 7.2 Validation Rules

CI **MUST** fail if:

1. ✗ Multiple metadata blocks present
2. ✗ RAW_DATA without meeting all requirements
3. ✗ API data classified as RAW_DATA
4. ✗ Unsupported agency used
5. ✗ MD5 checksum used anywhere
6. ✗ Missing visual attributes
7. ✗ Missing required fields
8. ✗ Checksum mismatch

### 7.3 Validation Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All validation passed |
| 1 | Validation failures found |

---

## 8. AUDIT AND STATUS REPORTING

### 8.1 Audit Report

**Generated by:** `scripts/generate_audit.py`  
**Output:** `docs/audit/AGENCY_CONNECTIVITY_AUDIT.json`

**Purpose:**
- Machine-readable connectivity status
- Endpoint inventory
- Coverage analysis

### 8.2 Status Document

**Generated by:** `scripts/generate_status.py`  
**Output:** `docs/status/AGENCY_CONNECTIVITY_STATUS.md`

**Purpose:**
- Human-readable status table
- Agency-by-agency breakdown
- Implementation status

### 8.3 Regeneration Requirement

Both audit and status documents **MUST** be regenerated:
- On every configuration change
- On every CI run (recommended)
- On demand via script execution

---

## 9. COMMUNICATION POLICY

**IMPORTANT:** TRIZEL-AI does not provide direct messaging.

**All communication is conducted through verifiable channels:**
- GitHub (issues, pull requests, discussions)
- ORCID (research profiles)
- DOI-linked archival records (Zenodo, OSF, HAL)

**No other communication channels are authorized.**

---

## 10. CHECKSUM POLICY

### 10.1 Required Algorithm

**SHA-256:** REQUIRED for all data files and downloads

### 10.2 Forbidden Algorithms

**MD5:** ABSOLUTELY FORBIDDEN
- Cryptographically broken
- CI must fail if detected
- No exceptions

### 10.3 Future Extensions

**SHA-512:** May be added as optional additional verification

---

## 11. ACCEPTANCE CRITERIA

This governance framework is considered successfully implemented when:

### 11.1 Agency Coverage
- ✓ Japan (JAXA) explicitly present in registry
- ✓ China (CNSA) explicitly present with "Monitoring" status and limitation documented
- ✓ Russia (ROSCOSMOS) explicitly present with "Monitoring" status and limitation documented

### 11.2 Download Capability
- ✓ At least one real RAW dataset download implemented for at least one agency with public raw access
- ✓ Checksums + provenance stored for all downloads
- ✓ Sidecar metadata generated

### 11.3 Differentiation
- ✓ SNAPSHOT vs RAW_DATA cannot be confused (labels + validation + docs)
- ✓ Visual attributes consistently applied
- ✓ Warning labels present

### 11.4 Enforcement
- ✓ CI enforces all contracts
- ✓ CI blocks false RAW claims
- ✓ Validation comprehensive and automated

### 11.5 Documentation
- ✓ One authoritative governance document (this file)
- ✓ Supersession notice for old issues
- ✓ Status and audit documents generated

---

## 12. SUPERSESSION

This document **SUPERSEDES:**
- All previous governance documents
- All issue-based specifications
- All partial implementation notes

In case of conflict, **this document takes precedence**.

See `docs/governance/SUPERSESSION_NOTICE.md` for specific superseded items.

---

## 13. VERSION HISTORY

**1.0.0** (2026-01-10)
- Initial authoritative governance framework
- Consolidated agency registry
- RAW data download system
- Complete validation rules
- ATLAS pipeline integration

---

## 14. MAINTENANCE

This document is maintained under version control.

**Updates require:**
- Version number increment
- Update timestamp
- Change log entry
- Review and approval

---

**END OF GOVERNANCE FRAMEWORK**
