# Agency Endpoint Registry and Connectivity Guide

**TRIZEL Monitor - International Space Agency Integration**

This document provides a comprehensive mapping of official space agency endpoints for raw data acquisition and verification.

---

## Trusted Agency Whitelist

Only the following agencies are authorized to provide RAW_DATA classification:

| Agency | Full Name | Country | Status |
|--------|-----------|---------|--------|
| NASA | National Aeronautics and Space Administration | USA | ✓ Active |
| ESA | European Space Agency | Europe | ✓ Active |
| CNSA | China National Space Administration | China | ⚠ Limited |
| Roscosmos | Roscosmos State Corporation | Russia | ⚠ Limited |
| JAXA | Japan Aerospace Exploration Agency | Japan | ✓ Active |
| MPC | Minor Planet Center (IAU) | International | ✓ Active |

---

## NASA Endpoints

### NASA JPL Small-Body Database (SBDB) API
- **URL**: https://ssd-api.jpl.nasa.gov/sbdb.api
- **Type**: API (Snapshot)
- **Data Type**: Orbital elements, physical parameters
- **Classification**: SNAPSHOT (computed/aggregated data, not raw observations)
- **License**: Public Domain
- **Documentation**: https://ssd-api.jpl.nasa.gov/doc/sbdb.html
- **Real-time**: No (delayed aggregation)

### NASA JPL Horizons System
- **URL**: https://ssd.jpl.nasa.gov/api/horizons.api
- **Type**: API (Computed)
- **Data Type**: Ephemerides, vectors, observer geometry
- **Classification**: DERIVED (computed from orbital elements)
- **License**: Public Domain
- **Documentation**: https://ssd-api.jpl.nasa.gov/doc/horizons.html

### NASA Planetary Data System (PDS)
- **URL**: https://pds.nasa.gov/
- **Type**: Archive (Raw Data)
- **Data Type**: Mission observations (raw and calibrated)
- **Classification**: RAW_DATA (mission telemetry and observations)
- **License**: Public Domain
- **Access**: Query-based, mission-specific endpoints
- **Note**: PDS contains actual mission data archives

---

## ESA Endpoints

### XMM-Newton Science Archive (XSA)
- **URL**: https://www.cosmos.esa.int/web/xmm-newton
- **Type**: Archive (Raw Data)
- **Data Type**: X-ray observations
- **Classification**: RAW_DATA (telescope observations)
- **License**: ESA data policy (public access)
- **Access**: Query via XSA portal
- **Real-time**: No (mission archive)

### ESA Science Archives
- **URL**: https://www.cosmos.esa.int/
- **Type**: Multi-mission archive
- **Data Type**: Various mission data
- **Classification**: RAW_DATA (mission archives)
- **License**: ESA data policy

---

## JAXA Endpoints

### JAXA DARTS (Data ARchives and Transmission System)
- **URL**: https://darts.isas.jaxa.jp/
- **Type**: Archive (Raw Data)
- **Data Type**: Mission observations and data products
- **Classification**: RAW_DATA (mission archives)
- **License**: JAXA data policy
- **Access**: Web interface and API
- **Missions**: Hayabusa, Akatsuki, XRISM, etc.

---

## CNSA Endpoints

### CNSA Official Portal
- **URL**: http://www.cnsa.gov.cn/
- **Type**: Portal (Informational)
- **Data Type**: Mission announcements, news
- **Classification**: Not applicable (no direct data access)
- **Note**: Data availability varies by mission and release channel
- **Status**: Limited public API access

---

## Roscosmos Endpoints

### Roscosmos Official Portal
- **URL**: https://www.roscosmos.ru/
- **Type**: Portal (Informational)
- **Data Type**: Mission information, announcements
- **Classification**: Not applicable (no direct data access)
- **Note**: Limited public API infrastructure
- **Status**: Primarily informational

---

## MPC (Minor Planet Center)

### MPC Database
- **URL**: https://www.minorplanetcenter.net/
- **Type**: Registry and Archive
- **Data Type**: Astrometry, orbital elements
- **Classification**: RAW_DATA (submitted observations) + DERIVED (computed orbits)
- **License**: IAU/MPC data policy
- **Access**: Web services and bulk downloads
- **Real-time**: Near real-time (observers submit observations)

---

## Data Classification Rules by Source

### RAW_DATA Sources
- PDS mission archives (NASA)
- ESA mission archives (XMM-Newton, etc.)
- JAXA DARTS mission data
- MPC observational submissions
- Direct telescope/instrument data

### SNAPSHOT Sources
- JPL SBDB API (computed orbital parameters)
- Aggregated summary databases
- Processed catalogs
- Secondary compilations

### DERIVED Sources
- JPL Horizons (computed ephemerides)
- Orbit propagation results
- Model outputs
- Statistical analyses

---

## Integration Status

| Agency | Endpoints Defined | API Available | Raw Data Access | Integration Status |
|--------|------------------|---------------|-----------------|-------------------|
| NASA | 3 | ✓ Yes | ✓ Via PDS | Active |
| ESA | 2 | ✓ Yes | ✓ Via XSA | Active |
| JAXA | 1 | ✓ Yes | ✓ Via DARTS | Active |
| CNSA | 1 | ⚠ Limited | ⚠ Varies | Monitoring |
| Roscosmos | 1 | ⚠ Limited | ⚠ Limited | Monitoring |
| MPC | 1 | ✓ Yes | ✓ Yes | Active |

---

## Future Expansion

### Planned Integrations
- Ground-based observatories (ESO, Keck, etc.)
- Additional NASA archives (MAST, HEASARC)
- International collaborative facilities

### Requirements for New Sources
1. Official agency/institution endpoint
2. Public data policy
3. Verifiable provenance
4. Downloadable data products
5. Documented API or access method

---

## Usage in TRIZEL Monitor

The system automatically:
1. Classifies data based on source endpoint
2. Validates agency against whitelist
3. Applies appropriate metadata
4. Enforces downloadability for RAW_DATA
5. Requires provenance documentation

See `src/data_classification.py` for implementation details.

---

## Verification Checklist

Before accepting data as RAW_DATA:
- [ ] Source is official agency endpoint
- [ ] Agency is in trusted whitelist
- [ ] Data is directly downloadable
- [ ] Provenance chain is documented
- [ ] Checksum/integrity verification available
- [ ] License terms are clear
- [ ] NOT derived/computed/aggregated

---

## Contact and Updates

This registry is maintained as part of TRIZEL Monitor.

For updates to agency endpoints or new integrations, consult:
- NASA API documentation: https://api.nasa.gov/
- ESA data policy: https://www.esa.int/
- JAXA DARTS: https://darts.isas.jaxa.jp/
- MPC services: https://www.minorplanetcenter.net/

**Last Updated**: 2026-01-10
**Registry Version**: 1.0
