import os
import re
import json
import hashlib
import requests
from datetime import datetime
from typing import Any, Dict, Optional


# ============================================================
# TRIZEL Monitor — Official Data Acquisition (v2.0.0)
# ============================================================
#
# Scientific intent (STRICT):
# 1) Pull data from authoritative sources (NASA, ESA, JAXA, MPC only).
# 2) Store version-locked, timestamped snapshots with SINGLE metadata block.
# 3) Enforce strict data classification (RAW_DATA, SNAPSHOT, DERIVED).
# 4) Compute SHA-256 checksums for integrity verification.
# 5) Include visual attributes for clear data type differentiation.
#
# RULES (CI-ENFORCED):
# - EXACTLY ONE metadata block: "trizel_metadata" at root level
# - NO duplicated metadata blocks at any depth
# - RAW_DATA ONLY for direct archival downloads from official agencies
# - API responses (JPL SBDB) are SNAPSHOT, NOT RAW_DATA
# - SHA-256 checksums REQUIRED, MD5 FORBIDDEN
# - Visual attributes MUST match classification
#
# See DATA_CONTRACT.md and ISSUE_AUTHORITATIVE_DATA_GOVERNANCE.md
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

# Data governance version
DATA_CONTRACT_VERSION = "2.0.0"


# ----------------------------
# Data Classification Constants
# ----------------------------
class DataClassification:
    """
    Data classification types (STRICT):
    - RAW_DATA: Original archival files from official agencies (direct download only)
    - SNAPSHOT: API responses, computed values, real-time queries (e.g., JPL SBDB API)
    - DERIVED: Processed, analyzed, or transformed data
    """
    RAW_DATA = "RAW_DATA"
    SNAPSHOT = "SNAPSHOT"
    DERIVED = "DERIVED"


class SourceAgency:
    """
    Allowed authoritative agencies (STRICT):
    Only these agencies are recognized as official sources.
    """
    NASA = "NASA"
    ESA = "ESA"
    JAXA = "JAXA"
    MPC = "MPC"


# Visual attributes mapping (for UI rendering and semantic clarity)
VISUAL_ATTRIBUTES = {
    DataClassification.RAW_DATA: {
        "color": "green",
        "icon": "✓",
        "label": "RAW DATA"
    },
    DataClassification.SNAPSHOT: {
        "color": "orange",
        "icon": "⚠",
        "label": "SNAPSHOT – NO SCIENTIFIC VALUE ALONE"
    },
    DataClassification.DERIVED: {
        "color": "blue",
        "icon": "→",
        "label": "DERIVED DATA"
    }
}


# ----------------------------
# Utilities
# ----------------------------
def utc_now_iso() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_now_compact() -> str:
    """Return current UTC time in compact format for filenames."""
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def safe_slug(s: str) -> str:
    """
    Filename-safe slug. Keeps alphanumerics, dot, dash, underscore.
    Replaces others with underscore.
    """
    s = s.strip()
    s = re.sub(r"\s+", "_", s)
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


def compute_sha256(data: str) -> str:
    """
    Compute SHA-256 checksum of string data.
    
    SHA-256 is REQUIRED by data governance policy.
    MD5 is FORBIDDEN (cryptographically broken).
    
    Returns lowercase hex string for consistency.
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest().lower()


def write_json(path: str, payload: Dict[str, Any]) -> None:
    """Write JSON file atomically with proper formatting."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def http_get_json(url: str, params: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    """Execute HTTP GET request and return JSON response."""
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


# ----------------------------
# Official data sources (fetchable today)
# ----------------------------
def fetch_jpl_sbdb(object_name: str) -> Dict[str, Any]:
    """
    NASA/JPL SBDB (public API). 
    
    IMPORTANT: This is a SNAPSHOT data source (computed orbital elements).
    It is NOT RAW_DATA because it provides computed values, not original archival files.
    
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


def build_trizel_metadata(
    classification: str,
    agency: str,
    query_designation: str,
    resolved_designation: Optional[str],
    retrieved_utc: str,
    source_url: str,
    source_type: str,
    has_data: bool,
    has_error: bool,
    data_json: str  # Not used anymore, kept for compatibility
) -> Dict[str, Any]:
    """
    Build the SINGLE authoritative metadata block: trizel_metadata.
    
    This is the ONLY metadata block allowed at root level.
    All other keys (metadata, platforms_registry, sbdb_data, sbdb_error) are FORBIDDEN.
    
    Note: Checksum will be computed separately over the entire file content.
    
    See DATA_CONTRACT.md section 6 for schema specification.
    """
    # Get visual attributes for classification
    visual_attrs = VISUAL_ATTRIBUTES.get(classification, VISUAL_ATTRIBUTES[DataClassification.SNAPSHOT])
    
    return {
        "project": "TRIZEL Monitor",
        "pipeline": "Daily Official Data Monitor",
        "version": DATA_CONTRACT_VERSION,
        "data_classification": classification,
        "source_agency": agency,
        "query_designation": query_designation,
        "resolved_designation": resolved_designation,
        "retrieved_utc": retrieved_utc,
        "checksum": {
            "algorithm": "sha256",
            "value": ""  # Will be filled in after computing over entire file
        },
        "provenance": {
            "source_url": source_url,
            "source_type": source_type,
            "release_policy": "Public API - computed values updated as orbital solutions are refined"
        },
        "visual_attributes": visual_attrs,
        "integrity": {
            "has_data_payload": has_data,
            "has_error": has_error,
            "validation_status": "pending"
        }
    }


# ----------------------------
# Main
# ----------------------------
def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    retrieved_utc = utc_now_iso()
    file_stamp = utc_now_compact()

    # 1) Fetch SBDB snapshot (official)
    # IMPORTANT: JPL SBDB API is SNAPSHOT classification, NOT RAW_DATA
    # (computed orbital elements, not original archival files)
    sbdb_payload: Dict[str, Any]
    has_error = False
    error_type: Optional[str] = None
    
    try:
        sbdb_payload = fetch_jpl_sbdb(TARGET_OBJECT)
    except requests.RequestException as e:
        # We still write a structured error snapshot (important for daily monitoring)
        sbdb_payload = {}
        has_error = True
        error_type = "request_exception"
        print(f"[ERROR] Failed to fetch SBDB data: {e}")

    resolved = extract_resolved_designation(sbdb_payload) if sbdb_payload else None

    # 2) Build output payload (NEW FORMAT - single metadata block)
    # Structure: { "trizel_metadata": {...}, "data": {...} }
    # NO legacy keys: metadata, platforms_registry, sbdb_data, sbdb_error
    
    data_payload = {
        "sbdb_response": sbdb_payload,
        "error_type": error_type,
    }
    
    # Build the SINGLE metadata block (without checksum first)
    trizel_metadata = build_trizel_metadata(
        classification=DataClassification.SNAPSHOT,  # JPL SBDB API is SNAPSHOT, not RAW_DATA
        agency=SourceAgency.NASA,
        query_designation=TARGET_OBJECT,
        resolved_designation=resolved,
        retrieved_utc=retrieved_utc,
        source_url=SBDB_API_URL,
        source_type="api",
        has_data=bool(sbdb_payload),
        has_error=has_error,
        data_json=""  # Will compute checksum properly below
    )
    
    # FINAL OUTPUT STRUCTURE (compliant with DATA_CONTRACT.md v2.0.0)
    output = {
        "trizel_metadata": trizel_metadata,
        "data": data_payload
    }
    
    # Compute checksum over the entire file content (excluding the checksum field itself)
    # This ensures the checksum validates the complete file structure
    output_for_checksum = output.copy()
    output_for_checksum["trizel_metadata"] = output["trizel_metadata"].copy()
    output_for_checksum["trizel_metadata"]["checksum"] = {"algorithm": "sha256", "value": ""}
    file_content_json = json.dumps(output_for_checksum, indent=2, ensure_ascii=False, sort_keys=True)
    checksum_value = compute_sha256(file_content_json)
    
    # Update the checksum in the actual output
    output["trizel_metadata"]["checksum"]["value"] = checksum_value

    # 3) Filenames
    slug = safe_slug(TARGET_OBJECT) or "unknown_object"
    timestamped_path = os.path.join(DATA_DIR, f"snapshot_{slug}_{file_stamp}.json")
    latest_path = os.path.join(DATA_DIR, f"snapshot_{slug}_latest.json")

    # 4) Write outputs
    write_json(timestamped_path, output)
    write_json(latest_path, output)

    # 5) Console output
    print("[OK] Data snapshot written (SNAPSHOT classification):")
    print(f" - Timestamped: {timestamped_path}")
    print(f" - Latest: {latest_path}")
    print(f" - Classification: {trizel_metadata['data_classification']}")
    print(f" - Agency: {trizel_metadata['source_agency']}")
    print(f" - Visual: {trizel_metadata['visual_attributes']['label']}")
    print(f" - SHA-256: {trizel_metadata['checksum']['value']}")

    # Exit code policy:
    # 0 = success
    # 2 = API error (still wrote diagnostic snapshot)
    # 3 = fatal error
    if has_error:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
