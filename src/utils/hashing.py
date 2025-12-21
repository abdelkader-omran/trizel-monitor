"""
src/utils/hashing.py - File hashing and size utilities

Provides deterministic SHA-256 hashing and file size computation for integrity verification.
"""

import hashlib
import os
from typing import Union


def sha256_file(path: Union[str, os.PathLike]) -> str:
    """
    Compute SHA-256 hash of a file.
    
    Args:
        path: Path to the file
    
    Returns:
        str: Hexadecimal SHA-256 digest
    
    Raises:
        FileNotFoundError: If file does not exist
        IOError: If file cannot be read
    
    Examples:
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        ...     _ = f.write(b'test data')
        ...     temp_path = f.name
        >>> hash_val = sha256_file(temp_path)
        >>> len(hash_val) == 64  # SHA-256 produces 64 hex chars
        True
        >>> os.unlink(temp_path)
    """
    sha256_hash = hashlib.sha256()
    
    with open(path, "rb") as f:
        # Read in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def size_bytes(path: Union[str, os.PathLike]) -> int:
    """
    Get file size in bytes.
    
    Args:
        path: Path to the file
    
    Returns:
        int: File size in bytes
    
    Raises:
        FileNotFoundError: If file does not exist
    
    Examples:
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        ...     _ = f.write(b'test')
        ...     temp_path = f.name
        >>> size_bytes(temp_path)
        4
        >>> os.unlink(temp_path)
    """
    return os.path.getsize(path)
