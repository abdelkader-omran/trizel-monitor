"""
Data Classification and Metadata Framework
TRIZEL Monitor - Raw Data Archival Integrity

Scientific Rule: A dataset has scientific value ONLY if it is explicitly 
identified as RAW DATA, traceable to an official space agency source, 
independently downloadable, and verifiable.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import json


class DataClass(Enum):
    """Mutually exclusive data classification classes"""
    RAW_DATA = "RAW_DATA"
    SNAPSHOT = "SNAPSHOT"
    DERIVED = "DERIVED"


class TrustedAgency(Enum):
    """Whitelist of official space agencies for RAW_DATA classification"""
    NASA = "NASA"
    ESA = "ESA"
    CNSA = "CNSA"
    ROSCOSMOS = "Roscosmos"
    JAXA = "JAXA"
    MPC = "MPC"  # Minor Planet Center (IAU)


# Agency endpoint registry with verified official URLs
AGENCY_ENDPOINTS: Dict[str, Dict[str, Any]] = {
    "NASA": {
        "name": "NASA",
        "full_name": "National Aeronautics and Space Administration",
        "country": "USA",
        "endpoints": {
            "SBDB": {
                "url": "https://ssd-api.jpl.nasa.gov/sbdb.api",
                "description": "Small-Body Database API",
                "type": "api",
                "data_type": "orbital_elements_physical_parameters",
                "is_raw_data_source": False,  # API snapshots, not raw observations
            },
            "Horizons": {
                "url": "https://ssd.jpl.nasa.gov/api/horizons.api",
                "description": "Horizons System API",
                "type": "api",
                "data_type": "ephemerides",
                "is_raw_data_source": False,  # Computed ephemerides
            },
            "PDS": {
                "url": "https://pds.nasa.gov/",
                "description": "Planetary Data System",
                "type": "archive",
                "data_type": "mission_data",
                "is_raw_data_source": True,  # Raw mission data
            },
        },
    },
    "ESA": {
        "name": "ESA",
        "full_name": "European Space Agency",
        "country": "Europe",
        "endpoints": {
            "XMM-Newton": {
                "url": "https://www.cosmos.esa.int/web/xmm-newton",
                "description": "XMM-Newton Science Archive",
                "type": "archive",
                "data_type": "x_ray_observations",
                "is_raw_data_source": True,
            },
            "ESA_Archives": {
                "url": "https://www.cosmos.esa.int/",
                "description": "ESA Science Archives",
                "type": "archive",
                "data_type": "mission_data",
                "is_raw_data_source": True,
            },
        },
    },
    "CNSA": {
        "name": "CNSA",
        "full_name": "China National Space Administration",
        "country": "China",
        "endpoints": {
            "CNSA_Portal": {
                "url": "http://www.cnsa.gov.cn/",
                "description": "CNSA Official Portal",
                "type": "portal",
                "data_type": "mission_announcements",
                "is_raw_data_source": False,  # Announcements, not data
                "note": "Data availability varies by release channel",
            },
        },
    },
    "Roscosmos": {
        "name": "Roscosmos",
        "full_name": "Roscosmos State Corporation",
        "country": "Russia",
        "endpoints": {
            "Roscosmos_Portal": {
                "url": "https://www.roscosmos.ru/",
                "description": "Roscosmos Official Portal",
                "type": "portal",
                "data_type": "mission_information",
                "is_raw_data_source": False,
                "note": "Limited public API access",
            },
        },
    },
    "JAXA": {
        "name": "JAXA",
        "full_name": "Japan Aerospace Exploration Agency",
        "country": "Japan",
        "endpoints": {
            "JAXA_DARTS": {
                "url": "https://darts.isas.jaxa.jp/",
                "description": "Data ARchives and Transmission System",
                "type": "archive",
                "data_type": "mission_data",
                "is_raw_data_source": True,
            },
        },
    },
    "MPC": {
        "name": "MPC",
        "full_name": "Minor Planet Center",
        "country": "International (IAU)",
        "endpoints": {
            "MPC_API": {
                "url": "https://www.minorplanetcenter.net/",
                "description": "MPC Database",
                "type": "registry",
                "data_type": "astrometry_orbits",
                "is_raw_data_source": True,
            },
        },
    },
}


class DataMetadata:
    """Mandatory metadata structure for all data files"""
    
    def __init__(
        self,
        data_class: DataClass,
        source_agency: str,
        agency_endpoint: str,
        license_info: str,
        delay_policy: Dict[str, Any],
        retrieval_timestamp: str,
        target_object: str,
        checksum: Optional[str] = None,
        download_url: Optional[str] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ):
        self.data_class = data_class
        self.source_agency = source_agency
        self.agency_endpoint = agency_endpoint
        self.license_info = license_info
        self.delay_policy = delay_policy
        self.retrieval_timestamp = retrieval_timestamp
        self.target_object = target_object
        self.checksum = checksum
        self.download_url = download_url
        self.provenance = provenance or {}
        
        # Validate at construction
        self._validate()
    
    def _validate(self) -> None:
        """Validate metadata completeness and consistency"""
        # All fields must be non-empty
        if not self.source_agency:
            raise ValueError("source_agency is mandatory")
        if not self.agency_endpoint:
            raise ValueError("agency_endpoint is mandatory")
        if not self.license_info:
            raise ValueError("license_info is mandatory")
        if not self.delay_policy:
            raise ValueError("delay_policy is mandatory")
        if not self.retrieval_timestamp:
            raise ValueError("retrieval_timestamp is mandatory")
        
        # RAW_DATA requires downloadability
        if self.data_class == DataClass.RAW_DATA:
            if not self.download_url:
                raise ValueError("RAW_DATA requires download_url")
            if not self.provenance:
                raise ValueError("RAW_DATA requires provenance information")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "data_class": self.data_class.value,
            "source_agency": self.source_agency,
            "agency_endpoint": self.agency_endpoint,
            "license": self.license_info,
            "delay_policy": self.delay_policy,
            "retrieval_timestamp": self.retrieval_timestamp,
            "target_object": self.target_object,
            "checksum": self.checksum,
            "download_url": self.download_url,
            "provenance": self.provenance,
            "visual_attributes": self._get_visual_attributes(),
        }
    
    def _get_visual_attributes(self) -> Dict[str, str]:
        """Visual distinction attributes for UI rendering"""
        if self.data_class == DataClass.RAW_DATA:
            return {
                "label": "RAW DATA — OFFICIAL AGENCY SOURCE",
                "color": "#00AA00",  # Green
                "badge": "✓ RAW",
                "icon": "verified",
                "resolution_flag": "VERIFIED",
            }
        elif self.data_class == DataClass.SNAPSHOT:
            return {
                "label": "SNAPSHOT — DERIVATIVE DATA",
                "color": "#FFA500",  # Orange
                "badge": "⚠ SNAPSHOT",
                "icon": "snapshot",
                "resolution_flag": "UNVERIFIED",
            }
        else:  # DERIVED
            return {
                "label": "DERIVED — COMPUTED DATA",
                "color": "#0088FF",  # Blue
                "badge": "→ DERIVED",
                "icon": "compute",
                "resolution_flag": "COMPUTED",
            }


def compute_checksum(data: Any) -> str:
    """
    Compute SHA256 checksum of data for integrity verification
    
    Args:
        data: JSON-serializable data structure
    
    Returns:
        Hexadecimal SHA256 checksum
    """
    json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


def classify_data_source(
    endpoint_url: str,
    agency: Optional[str] = None
) -> DataClass:
    """
    Classify data based on source endpoint
    
    Scientific Rule: if source ≠ official agency raw endpoint → RAW_DATA = false
    
    Args:
        endpoint_url: The URL or endpoint being accessed
        agency: Optional agency name
    
    Returns:
        DataClass classification
    """
    # Check if endpoint is a verified raw data source
    if agency and agency in AGENCY_ENDPOINTS:
        agency_info = AGENCY_ENDPOINTS[agency]
        for endpoint_name, endpoint_data in agency_info.get("endpoints", {}).items():
            if endpoint_data.get("url") in endpoint_url:
                if endpoint_data.get("is_raw_data_source", False):
                    return DataClass.RAW_DATA
    
    # Default: SNAPSHOT (computed/derivative data from APIs)
    return DataClass.SNAPSHOT


def validate_agency(agency_name: str) -> bool:
    """
    Validate that agency is in trusted whitelist
    
    Args:
        agency_name: Name of the agency
    
    Returns:
        True if agency is trusted, False otherwise
    """
    try:
        TrustedAgency[agency_name.upper().replace(" ", "_")]
        return True
    except KeyError:
        return False


def create_default_delay_policy(is_real_time: bool = False) -> Dict[str, Any]:
    """
    Create delay policy metadata
    
    Scientific assumption: NO real-time raw data by default
    
    Args:
        is_real_time: Override flag (requires agency proof)
    
    Returns:
        Delay policy dictionary
    """
    return {
        "raw_release_delay": not is_real_time,
        "is_real_time_claim": is_real_time,
        "default_assumption": "delayed_release",
        "note": "Real-time claims require explicit agency documentation",
    }
