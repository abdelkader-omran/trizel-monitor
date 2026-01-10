import os
import re
import json
import requests
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Import data classification framework
from data_classification import (
    DataClass,
    DataMetadata,
    compute_checksum,
    classify_data_source,
    create_default_delay_policy,
    AGENCY_ENDPOINTS,
)


# ============================================================
# TRIZEL Monitor — Official Data Acquisition (Auto DZ ACT ready)
# ============================================================
#
# Scientific intent (strict):
# 1) Pull an authoritative orbital/physical snapshot from an official public endpoint (JPL SBDB).
# 2) Store a version-locked, timestamped snapshot + a stable "latest" snapshot.
# 3) Record a "global platforms registry" (agencies/observatories) as evidence targets:
#    not all platforms are machine-fetchable; we keep them as citable sources and expand later.
#
# NOTE:
# - For interstellar objects, naming/availability can vary by registry. We preserve both:
#   query_designation (user input) + resolved_designation (if the API returns one).
# - This script is data-acquisition only. Auto DZ ACT evaluation should be a separate step/module.
# ============================================================


# ----------------------------
# Configuration (one-time)
# ----------------------------
DATA_DIR = os.getenv("DATA_DIR", "data").strip() or "data"
SBDB_API_URL = os.getenv("SBDB_API_URL", "https://ssd-api.jpl.nasa.gov/sbdb.api").strip()

# Set once via GitHub Actions env, do not edit code each run:
#   TARGET_OBJECT: e.g., "3I/ATLAS" or "1I/'Oumuamua"
TARGET_OBJECT = os.getenv("TARGET_OBJECT", "3I/ATLAS").strip()

# Network/timeouts
HTTP_TIMEOUT_SEC = int(os.getenv("HTTP_TIMEOUT_SEC", "30"))


# ----------------------------
# Utilities
# ----------------------------
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def safe_slug(s: str) -> str:
    """
    Filename-safe slug. Keeps alphanumerics, dot, dash, underscore.
    Replaces others with underscore.
    """
    s = s.strip()
    s = re.sub(r"\s+", "_", s)
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


def write_json(path: str, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def http_get_json(url: str, params: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ----------------------------
# Official data sources (fetchable today)
# ----------------------------
def fetch_jpl_sbdb(object_name: str) -> Dict[str, Any]:
    """
    NASA/JPL SBDB (public API). Authoritative for orbital context in many workflows.

    We request:
    - orb=1: orbital elements
    - phys-par=1: physical parameters if available
    """
    params = {
        "sstr": object_name,
        "orb": "1",
        "phys-par": "1",
    }
    return http_get_json(SBDB_API_URL, params=params, timeout=HTTP_TIMEOUT_SEC)


def extract_resolved_designation(sbdb_json: Dict[str, Any]) -> Optional[str]:
    """
    Best-effort extraction of an official designation from SBDB response.
    SBDB structures vary by object; we keep this defensive.
    """
    # Common patterns in SBDB payloads (may differ by object/type)
    for key_path in [
        ("object", "des"),
        ("object", "fullname"),
        ("object", "name"),
        ("object", "spkid"),
    ]:
        node: Any = sbdb_json
        ok = True
        for k in key_path:
            if isinstance(node, dict) and k in node:
                node = node[k]
            else:
                ok = False
                break
        if ok and node is not None:
            return str(node)
    return None


# ----------------------------
# Global platforms registry (citable, expandable)
# ----------------------------
def global_platforms_registry() -> Dict[str, Any]:
    """
    This is NOT "fetched data"; it is a structured registry of official platforms
    relevant to 3I/ATLAS monitoring and Auto DZ ACT evidence-tracing.

    We store it so each run produces a versioned snapshot of what the pipeline considers
    an admissible official platform. You can add/remove entries without changing the
    SBDB acquisition logic.
    """
    return {
        "intent": "Evidence & archive targets (official platforms). Not all are machine-fetchable via API.",
        "categories": {
            "authoritative_orbit_and_astrometry": [
                {"name": "Minor Planet Center (MPC)", "role": "IAU clearinghouse for astrometry/orbits", "type": "registry"},
                {"name": "NASA/JPL SSD SBDB", "role": "public small-body database API", "type": "api"},
                {"name": "NASA/JPL Horizons", "role": "ephemerides / vectors / observer geometry", "type": "service"},
            ],
            "major_space_agencies_and_missions": [
                {"name": "ESA", "role": "missions + archives (e.g., XMM-Newton)", "type": "agency"},
                {"name": "ESO", "role": "ground-based observatory archives (e.g., VLT instruments)", "type": "observatory"},
                {"name": "JAXA", "role": "missions + archives (e.g., XRISM collaboration context)", "type": "agency"},
                {"name": "CNSA", "role": "missions/announcements; data availability varies by release channel", "type": "agency"},
                {"name": "NASA", "role": "missions + archives (e.g., HST/JWST where relevant)", "type": "agency"},
            ],
            "space_and_ground_archives": [
                {"name": "MAST (HST/JWST)", "role": "space telescope archive", "type": "archive"},
                {"name": "ESO Science Archive", "role": "ESO observational archive", "type": "archive"},
                {"name": "HEASARC", "role": "high-energy mission archive gateway (where applicable)", "type": "archive"},
                {"name": "XMM-Newton Science Archive (XSA)", "role": "XMM data archive (ESA)", "type": "archive"},
            ],
        },
        "policy": {
            "verification_first": "Every claim used by Auto DZ ACT should cite a primary dataset record (ObsID/DOI/solution id).",
            "no_unverifiable_claims": "If a platform has no public DOI/ObsID/product, it is tracked as 'media-only' until operationalized.",
        },
    }


# ----------------------------
# Main
# ----------------------------
def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    retrieved_utc = utc_now_iso()
    file_stamp = utc_now_compact()

    # 1) Fetch SBDB snapshot (official)
    sbdb_payload: Dict[str, Any]
    sbdb_error: Optional[Dict[str, Any]] = None
    try:
        sbdb_payload = fetch_jpl_sbdb(TARGET_OBJECT)
    except requests.RequestException as e:
        # We still write a structured error snapshot (important for daily monitoring)
        sbdb_payload = {}
        sbdb_error = {
            "type": "request_error",
            "message": str(e),
        }

    resolved = extract_resolved_designation(sbdb_payload) if sbdb_payload else None

    # 2) Build metadata (Auto DZ ACT compatible)
    metadata = {
        "project": "TRIZEL Monitor",
        "pipeline": "Daily Official Data Monitor",
        "query_designation": TARGET_OBJECT,
        "resolved_designation": resolved,
        "retrieved_utc": retrieved_utc,
        "sources": {
            "sbdb": SBDB_API_URL,
            "note": "SBDB is used as an official orbit/phys snapshot endpoint in this acquisition step.",
        },
        "integrity": {
            "has_sbdb_payload": bool(sbdb_payload),
            "has_error": sbdb_error is not None,
        },
    }
    
    # 2b) Build data classification metadata (NEW: Raw Data Archival Integrity)
    # Classify data source - SBDB API returns computed snapshots, not raw observations
    data_class = classify_data_source(SBDB_API_URL, "NASA")
    
    # Create comprehensive data classification metadata
    data_classification_metadata = DataMetadata(
        data_class=data_class,
        source_agency="NASA",
        agency_endpoint=SBDB_API_URL,
        license_info="Public Domain (NASA data policy: https://www.nasa.gov/nasa-data-and-information-policy/)",
        delay_policy=create_default_delay_policy(is_real_time=False),
        retrieval_timestamp=retrieved_utc,
        target_object=TARGET_OBJECT,
        checksum=None,  # Will be computed after building full payload
        download_url=None if data_class == DataClass.SNAPSHOT else SBDB_API_URL,
        provenance={
            "source_type": "api_snapshot",
            "retrieval_method": "http_get",
            "api_version": "sbdb.api",
            "verification_status": "snapshot_derivative",
            "note": "SBDB provides computed orbital elements and physical parameters, not raw observational data. This is a SNAPSHOT of processed information.",
        },
    )

    # 3) Full output payload (version-lock snapshot)
    output = {
        "metadata": metadata,
        "data_classification": data_classification_metadata.to_dict(),
        "platforms_registry": global_platforms_registry(),
        "agency_endpoints": AGENCY_ENDPOINTS,
        "sbdb_data": sbdb_payload,
        "sbdb_error": sbdb_error,
    }
    
    # 3b) Compute and update checksum after building full output
    checksum = compute_checksum(output)
    data_classification_metadata.checksum = checksum
    output["data_classification"]["checksum"] = checksum

    # 4) Filenames
    slug = safe_slug(TARGET_OBJECT) or "unknown_object"
    timestamped_path = os.path.join(DATA_DIR, f"official_snapshot_{slug}_{file_stamp}.json")
    latest_path = os.path.join(DATA_DIR, "official_snapshot_latest.json")
    registry_path = os.path.join(DATA_DIR, f"platforms_registry_{file_stamp}.json")

    # 5) Write outputs
    write_json(timestamped_path, output)
    write_json(latest_path, output)
    write_json(registry_path, output["platforms_registry"])

    # 6) Console
    print("[OK] Official data snapshot written:")
    print(f" - {timestamped_path}")
    print(f" - {latest_path}")
    print(f"[OK] Platforms registry snapshot written:")
    print(f" - {registry_path}")

    # Exit code policy:
    # If SBDB fails, we keep a snapshot (for monitoring), but mark failure via non-zero exit.
    # This helps you see failures in Actions while still preserving diagnostics.
    if sbdb_error is not None:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
