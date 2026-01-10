# TRIZEL Monitor - Agency Connectivity Status

**Generated:** 2026-01-10 19:23:29 UTC  
**Source:** `config/agency_registry.json`

## Overview

This document provides the current status of international space agency connectivity
for the TRIZEL Monitor raw data archive system.

## Status Definitions

- **Active:** Publicly downloadable RAW datasets exist and are implemented in download system
- **Monitoring:** Agency exists but raw download not implemented or not publicly accessible without credentials
- **Limited:** Only catalogs/metadata or derived products available without authentication

## Visual Attributes Legend

| Data Type | Color | Icon | Label |
|-----------|-------|------|-------|
| RAW_DATA | 🟢 Green | ✓ | RAW DATA |
| SNAPSHOT | 🟠 Orange | ⚠ | SNAPSHOT – NO SCIENTIFIC VALUE ALONE |
| DERIVED | 🔵 Blue | → | DERIVED DATA |

## Agency Status Table

| Agency | Full Name | Country | Status | Raw Data | Endpoints | Notes |
|--------|-----------|---------|--------|----------|-----------|-------|
| NASA | National Aeronautics and Space Administration | United States | 🟢 Active | ✓ | 2 | Multiple public raw data archives available |
| ESA | European Space Agency | Europe | 🟢 Active | ✓ | 1 | Public archives available through ESA Science Archives |
| JAXA | Japan Aerospace Exploration Agency | Japan | 🟢 Active | ✓ | 1 | DARTS (Data ARchives and Transmission System) provides public access to mission data |
| CNSA | China National Space Administration | China | 🟡 Monitoring | ✗ | 1 | Limited public raw data access. Most datasets require formal data request and institutional credentials. Monitoring official announcements and catalog updates. |
| ROSCOSMOS | Russian Federal Space Agency | Russia | 🟡 Monitoring | ✗ | 1 | Limited public raw data infrastructure. Most archival data requires institutional access or formal agreements. Monitoring official channels for public releases. |
| MPC | Minor Planet Center (IAU) | International | 🟢 Active | ✓ | 1 | Public access to astrometric observations and orbital elements |

## Detailed Endpoint Information

### NASA - National Aeronautics and Space Administration

| Endpoint | Type | URL | Auth Required | Download Mode |
|----------|------|-----|---------------|---------------|
| JPL Small-Body Database API | 🟠 SNAPSHOT | https://ssd-api.jpl.nasa.gov/sbdb.api | No | API_JSON |
| Planetary Data System - Small Bodies Node | 🟢 RAW_DATA | https://pds-smallbodies.astro.umd.edu/ | No | DIRECT_FILE |

### ESA - European Space Agency

| Endpoint | Type | URL | Auth Required | Download Mode |
|----------|------|-----|---------------|---------------|
| ESA Science Archives | 🟢 RAW_DATA | https://archives.esac.esa.int/ | No | DIRECT_FILE |

### JAXA - Japan Aerospace Exploration Agency

| Endpoint | Type | URL | Auth Required | Download Mode |
|----------|------|-----|---------------|---------------|
| JAXA DARTS | 🟢 RAW_DATA | https://darts.isas.jaxa.jp/ | No | DIRECT_FILE |

### CNSA - China National Space Administration

| Endpoint | Type | URL | Auth Required | Download Mode |
|----------|------|-----|---------------|---------------|
| CNSA Official Announcements | 📋 CATALOG | http://www.cnsa.gov.cn/english/ | No | HTML_INDEX |

### ROSCOSMOS - Russian Federal Space Agency

| Endpoint | Type | URL | Auth Required | Download Mode |
|----------|------|-----|---------------|---------------|
| ROSCOSMOS Official Portal | 📋 CATALOG | https://www.roscosmos.ru/ | No | HTML_INDEX |

### MPC - Minor Planet Center (IAU)

| Endpoint | Type | URL | Auth Required | Download Mode |
|----------|------|-----|---------------|---------------|
| MPC Observations Database | 🟢 RAW_DATA | https://www.minorplanetcenter.net/db_search | No | DIRECT_FILE |

## Implementation Status

### Coverage Summary

- **Total Agencies:** 6
- **Active (with raw data access):** 4
- **Monitoring (limited access):** 2
- **Agencies with raw data capability:** 4

### Required Coverage Verification

- ✓ **Japan (JAXA):** Present
- ✓ **China (CNSA):** Present
- ✓ **Russia (ROSCOSMOS):** Present

---

*This document is automatically generated from the authoritative agency registry.*  
*Last update: 2026-01-10 19:23:29 UTC*
