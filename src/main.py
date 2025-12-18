import os
import json
from datetime import datetime

# Function to fetch data from NASA / JPL SBDB (mock implementation; replace with actual logic)
def fetch_data_from_nasa():
    # Replace this mock data fetching with actual API calls and logic.
    return {
        "object": "ExampleObject",
        "data": {
            "property1": "value1",
            "property2": "value2"
        }
    }

# Ensure the 'data/' directory exists
data_directory = "data/"
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# Fetch the data
data_fetched = fetch_data_from_nasa()

# Add metadata fields
retrieved_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
metadata = {
    "source": "NASA / JPL SBDB",
    "object": data_fetched.get("object"),
    "retrieved_utc": retrieved_timestamp
}

data_with_metadata = {**data_fetched, **metadata}

# Save the data in the two specified files
utc_timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
file_name_timestamped = os.path.join(data_directory, f"jpl_sbdb_{utc_timestamp}.json")
file_name_latest = os.path.join(data_directory, "latest_jpl_sbdb.json")

# Write the data with metadata to both files
with open(file_name_timestamped, "w") as file:
    json.dump(data_with_metadata, file, indent=4)

with open(file_name_latest, "w") as file:
    json.dump(data_with_metadata, file, indent=4)

print(f"Data saved to: {file_name_timestamped} and {file_name_latest}")