import pandas as pd
from pathlib import Path

# File path
raw_path = Path("Data/data.csv")        # Raw data
clean_dir = Path("cleanData")           # Clean data
clean_dir.mkdir(exist_ok=True)

clean_csv_path = clean_dir / "noise_complaints_clean.csv" 

# loading
print("Loading raw dataset...")

use_cols = [
    "Created Date", "Complaint Type",
    "Descriptor", "Borough",
    "Latitude", "Longitude"
]

df = pd.read_csv(
    raw_path,
    usecols=use_cols,
    low_memory=False
)

print(f"Raw data loaded. Total rows: {len(df):,}")

# 1.Retain only noise-related complaints
df = df[df["Complaint Type"].str.contains("noise", case=False, na=False)]
print(f"Filtered noise complaints. Rows remaining: {len(df):,}")

# 2.Administrative Area Name Cleanup
df["Borough"] = df["Borough"].str.strip().str.title()
invalid_boroughs = ["Unspecified", "", "None", "N/a"]
df = df[~df["Borough"].isin(invalid_boroughs)]
print(f"Cleaned borough names. Rows remaining: {len(df):,}")

# 3.Validate coordinate legality
nyc_lat_range = (40.477, 40.917)
nyc_lon_range = (-74.259, -73.700)

df = df[
    (df["Latitude"].between(*nyc_lat_range)) &
    (df["Longitude"].between(*nyc_lon_range))
]
# Unified Coordinate Accuracy
df["Latitude"] = df["Latitude"].round(6)
df["Longitude"] = df["Longitude"].round(6)

print(f"Valid spatial points remaining: {len(df):,}")

# 4.Key Field Missing Handling
df = df.drop_duplicates()
critical_cols = ["Borough", "Latitude", "Longitude", "Descriptor"]
df = df.dropna(subset=critical_cols)
print(f"Final cleaned dataset size: {len(df):,}")

# 5. Output the cleaned data
df.to_csv(clean_csv_path, index=False)
print("\nData cleaning completed successfully!")
print(f"Clean CSV saved to: {clean_csv_path}")

print("\npreview:")
print(df.head().to_string(index=False))
