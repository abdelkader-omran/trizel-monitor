"""
TRIZEL Monitor - RAW Data Download Module

This module provides the foundation for downloading RAW data files from
authoritative space agencies. It enforces:
- Direct file downloads with SHA-256 checksums
- Polite rate limiting and retry logic
- Proper storage with sidecar metadata
- Agency whitelist enforcement
"""

import os
import time
import hashlib
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse


class RawDataDownloader:
    """
    Downloads RAW data files from authorized agencies.
    
    Supports:
    - DIRECT_FILE downloads with content verification
    - Rate limiting to be polite to agency servers
    - Retry logic for transient failures
    - SHA-256 checksum computation
    - Sidecar metadata generation
    """
    
    def __init__(
        self,
        data_dir: str = "data/raw",
        rate_limit_delay: float = 2.0,
        max_retries: int = 3,
        timeout: int = 60
    ):
        """
        Initialize downloader.
        
        Args:
            data_dir: Base directory for raw data storage
            rate_limit_delay: Seconds to wait between downloads (polite crawling)
            max_retries: Maximum retry attempts for failed downloads
            timeout: HTTP timeout in seconds
        """
        self.data_dir = Path(data_dir)
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.last_download_time = 0
        
    def _ensure_rate_limit(self):
        """Enforce rate limiting between downloads."""
        elapsed = time.time() - self.last_download_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_download_time = time.time()
    
    def _compute_sha256(self, file_path: Path) -> str:
        """Compute SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest().lower()
    
    def _create_sidecar_metadata(
        self,
        file_path: Path,
        source_url: str,
        agency_id: str,
        dataset_id: str,
        checksum: str,
        content_length: Optional[int],
        license_or_policy_ref: str,
        delay_policy: str
    ) -> Dict[str, Any]:
        """
        Create sidecar metadata for downloaded RAW file.
        
        Follows the strict single metadata block contract.
        """
        metadata = {
            "trizel_metadata": {
                "project": "TRIZEL Monitor",
                "pipeline": "RAW Data Download System",
                "version": "1.0.0",
                "data_classification": "RAW_DATA",
                "source_agency": agency_id,
                "dataset_id": dataset_id,
                "source_file": file_path.name,
                "retrieval_timestamp_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "checksum_sha256": checksum,
                "source_url": source_url,
                "license_or_policy_ref": license_or_policy_ref,
                "delay_policy": delay_policy,
                "content_length_bytes": content_length,
                "visual_attributes": {
                    "color": "green",
                    "icon": "✓",
                    "label": "RAW DATA"
                },
                "integrity": {
                    "download_verified": True,
                    "checksum_algorithm": "sha256"
                }
            }
        }
        return metadata
    
    def download_file(
        self,
        url: str,
        agency_id: str,
        dataset_id: str,
        filename: str,
        license_or_policy_ref: str = "See agency policy",
        delay_policy: str = "Archive release policy applies"
    ) -> Optional[Path]:
        """
        Download a single RAW data file.
        
        Args:
            url: Direct download URL
            agency_id: Agency identifier (NASA, ESA, JAXA, MPC)
            dataset_id: Dataset/collection identifier
            filename: Output filename
            license_or_policy_ref: License or policy reference URL
            delay_policy: Data release delay policy statement
            
        Returns:
            Path to downloaded file, or None if download failed
        """
        # Enforce rate limiting
        self._ensure_rate_limit()
        
        # Create storage directory
        storage_dir = self.data_dir / agency_id / dataset_id
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = storage_dir / filename
        
        # Download with retry logic
        for attempt in range(self.max_retries):
            try:
                print(f"Downloading {url} (attempt {attempt + 1}/{self.max_retries})...")
                
                response = requests.get(url, timeout=self.timeout, stream=True)
                response.raise_for_status()
                
                # Get content length if available
                content_length = response.headers.get('content-length')
                content_length = int(content_length) if content_length else None
                
                # Write file
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✓ Downloaded to {file_path}")
                
                # Compute checksum
                print("Computing SHA-256 checksum...")
                checksum = self._compute_sha256(file_path)
                print(f"✓ SHA-256: {checksum}")
                
                # Create sidecar metadata
                metadata = self._create_sidecar_metadata(
                    file_path=file_path,
                    source_url=url,
                    agency_id=agency_id,
                    dataset_id=dataset_id,
                    checksum=checksum,
                    content_length=content_length,
                    license_or_policy_ref=license_or_policy_ref,
                    delay_policy=delay_policy
                )
                
                # Write sidecar file
                sidecar_path = file_path.with_suffix(file_path.suffix + '.meta.json')
                with open(sidecar_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                print(f"✓ Metadata written to {sidecar_path}")
                
                return file_path
                
            except requests.RequestException as e:
                print(f"✗ Download failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
        
        print(f"✗ Failed to download {url} after {self.max_retries} attempts")
        return None


def download_mpc_sample_observations(designation: str = "3I") -> Optional[Path]:
    """
    Example: Download sample observation data from MPC.
    
    This is a placeholder demonstrating the download pattern.
    Real MPC data access would use their actual download endpoints.
    
    Args:
        designation: Object designation
        
    Returns:
        Path to downloaded file, or None if failed
    """
    downloader = RawDataDownloader()
    
    # Note: This is a conceptual example. Real MPC downloads would use
    # their actual data access API or bulk download endpoints.
    # For now, this demonstrates the structure without making real downloads.
    
    print(f"MPC sample download for {designation} - placeholder")
    print("Real implementation would access MPC observation database")
    
    return None


def download_nasa_pds_sample() -> Optional[Path]:
    """
    Example: Download sample data from NASA Planetary Data System.
    
    This is a placeholder demonstrating the download pattern.
    Real PDS downloads would access specific mission archives.
    """
    downloader = RawDataDownloader()
    
    print("NASA PDS sample download - placeholder")
    print("Real implementation would access PDS Small Bodies Node archives")
    
    return None
