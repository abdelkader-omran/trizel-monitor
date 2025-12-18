"""
TRIZEL Monitor – Scientific Data Acquisition Core
-------------------------------------------------

Purpose:
    Initial real-data acquisition from official astronomical sources.

Scientific scope:
    - NASA / JPL Small-Body Database (SBDB)
    - Minor Planet Center (MPC)

Integrity rules:
    - No modification of original data
    - Full source attribution
    - Timestamped acquisition
"""

import requests
from datetime import datetime, timezone


def fetch_jpl_sbdb(object_name: str) -> dict:
    """
    Fetch official data from NASA JPL Small-Body Database.

    Reference:
    https://ssd-api.jpl.nasa.gov/doc/sbdb.html
    """
    url = "https://ssd-api.jpl.nasa.gov/sbdb.api"
    params = {"sstr": object_name}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    target_object = "3I/ATLAS"
    timestamp = datetime.now(timezone.utc).isoformat()

    data = fetch_jpl_sbdb(target_object)

    with open("latest_sbdb.json", "w", encoding="utf-8") as f:
        f.write(
            f"# Source: NASA JPL SBDB\n"
            f"# Object: {target_object}\n"
            f"# Retrieved: {timestamp}\n\n"
        )
        f.write(str(data))

    print("Scientific data successfully retrieved and archived.")


if __name__ == "__main__":
    main()
