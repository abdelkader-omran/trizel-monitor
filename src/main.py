import os
import json
import requests
from datetime import datetime


# =========================
# Configuration
# =========================

DATA_DIR = "data"
SBDB_API_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api"

# الجسم الافتراضي (يمكن تغييره لاحقًا)
TARGET_OBJECT = "1I/ʻOumuamua"


# =========================
# Data Acquisition
# =========================

def fetch_data_from_nasa_sbdb(object_name: str) -> dict:
    """
    Fetch real data from NASA / JPL Small-Body Database (SBDB)
    """
    params = {
        "sstr": object_name,
        "phys-par": "1",
        "orb": "1"
    }

    response = requests.get(SBDB_API_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


# =========================
# Main Execution
# =========================

def main():
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Fetch data from NASA / JPL
    nasa_data = fetch_data_from_nasa_sbdb(TARGET_OBJECT)

    # UTC timestamps
    retrieved_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    file_timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # Metadata layer (Auto Dz Act compatible)
    metadata = {
        "source": "NASA / JPL SBDB",
        "object_designation": TARGET_OBJECT,
        "retrieved_utc": retrieved_utc
    }

    # Merge raw data + metadata
    data_with_metadata = {
        "metadata": metadata,
        "sbdb_data": nasa_data
    }

    # Output files
    file_timestamped = os.path.join(
        DATA_DIR, f"sbdb_{TARGET_OBJECT.replace('/', '_')}_{file_timestamp}.json"
    )
    file_latest = os.path.join(
        DATA_DIR, "sbdb_latest.json"
    )

    # Write files
    with open(file_timestamped, "w", encoding="utf-8") as f:
        json.dump(data_with_metadata, f, indent=2, ensure_ascii=False)

    with open(file_latest, "w", encoding="utf-8") as f:
        json.dump(data_with_metadata, f, indent=2, ensure_ascii=False)

    print(f"[OK] NASA SBDB data saved:")
    print(f" - {file_timestamped}")
    print(f" - {file_latest}")


if __name__ == "__main__":
    main()
