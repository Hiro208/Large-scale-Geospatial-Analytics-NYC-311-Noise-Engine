import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.spatial import distance
from matplotlib.colors import LogNorm

# Set data and output paths
clean_dir = Path("cleanData")
output_dir = Path("output")

output_dir.mkdir(parents=True, exist_ok=True)
clean_csv_path = clean_dir / "noise_complaints_clean.csv"
print("Using cleaned CSV:", clean_csv_path)

# Load cleaned data
df = pd.read_csv(clean_csv_path)
df = df[df["Borough"].notna()]
print("Rows in cleaned data:", len(df))

# Count complaints by borough
print("\nCalculating borough complaint counts...")
borough_counts = df["Borough"].value_counts().sort_values(ascending=False)
print(borough_counts)

# Bar chart of complaint counts
plt.figure(figsize=(8, 5))
sns.barplot(
    x=borough_counts.index,
    y=borough_counts.values,
    hue=borough_counts.index,
    palette="deep",
    legend=False
)
plt.title("Noise Complaints by Borough (2025)", fontsize=14, fontweight="bold")
plt.xlabel("Borough")
plt.ylabel("Number of Complaints")
plt.tight_layout()
plt.savefig(output_dir / "borough_counts.png", dpi=300)
plt.close()

# Calculate complaint density
print("\nCalculating borough complaint density...")
borough_areas = {
    "Bronx": 109.3,
    "Brooklyn": 183.4,
    "Manhattan": 59.1,
    "Queens": 280.0,
    "Staten Island": 151.5
}

density_df = pd.DataFrame({
    "count": borough_counts,
    "area_sqkm": borough_counts.index.map(borough_areas)
})

density_df["density"] = density_df["count"] / density_df["area_sqkm"]
print("\nComplaint density (complaints per sq km):")
print(density_df.sort_values("density", ascending=False))

# Bar chart of complaint density
plt.figure(figsize=(8, 5))
sns.barplot(
    x=density_df.index,
    y=density_df["density"],
    hue=density_df.index,
    palette="viridis",
    legend=False
)
plt.title("Noise Complaint Density by Borough (per sq km)", fontsize=14, fontweight="bold")
plt.xlabel("Borough")
plt.ylabel("Complaints per Square Kilometer")
plt.tight_layout()
plt.savefig(output_dir / "borough_density.png", dpi=300)
plt.close()

# Analyze top noise descriptors
print("\nAnalyzing top descriptors...")
top5 = df["Descriptor"].value_counts().nlargest(5).index
df["Descriptor"] = df["Descriptor"].where(df["Descriptor"].isin(top5), "Other")

pivot = df.groupby(["Borough", "Descriptor"]).size().unstack(fill_value=0)
print("\nBorough × Descriptor Table:")
print(pivot)

# Stacked bar chart of noise types
plt.figure(figsize=(12, 6))
pivot.plot(kind="bar", stacked=True, colormap="tab20", figsize=(12, 6))
plt.title("Noise Complaint Descriptors by Borough (2025)", fontsize=14, fontweight="bold")
plt.xlabel("Borough")
plt.ylabel("Number of Complaints")
plt.tight_layout()
plt.savefig(output_dir / "borough_descriptor.png", dpi=300)
plt.close()

# Chi-square test
print("\nRunning Chi-square test...")
borough_sorted = df["Borough"].value_counts().sort_index()

k = len(borough_sorted)
total = borough_sorted.sum()
expected = np.repeat(total / k, k)

chi2 = (((borough_sorted.values - expected) ** 2) / expected).sum()
critical = 9.49

print("\nObserved:", borough_sorted.values)
print("Expected:", expected)
print("Chi-square:", chi2)

if chi2 > critical:
    print("Result: Reject H0 → Borough complaints differ significantly.")
else:
    print("Result: Fail to reject H0 → No significant difference.")

chi_df = pd.DataFrame({
    "Observed": borough_sorted.values,
    "Expected": expected
}, index=borough_sorted.index)

# Bar chart of observed vs expected
chi_df.plot(kind="bar", figsize=(8, 5))
plt.title("Observed vs Expected Noise Complaints by Borough", fontsize=14, fontweight="bold")
plt.xlabel("Borough")
plt.ylabel("Number of Complaints")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(output_dir / "chi_square_observed.png", dpi=300)
plt.close()

# Spatial scatter plot
print("\nPerforming spatial analysis...")
plt.figure(figsize=(8, 6))
sns.scatterplot(
    data=df,
    x="Longitude", y="Latitude",
    hue="Borough",
    s=1.2,
    linewidth=0,
    alpha=0.18,
    palette="tab10"
)
plt.title("Geographic Distribution of Noise Complaints", fontsize=14, fontweight="bold")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig(output_dir / "scatter_map.png", dpi=300)
plt.close()

# Spatial density heatmap
plt.figure(figsize=(8, 6))
heatmap, xedges, yedges = np.histogram2d(
    df["Longitude"],
    df["Latitude"],
    bins=60,
    range=[[-74.25, -73.70], [40.47, 40.92]]
)

plt.imshow(
    heatmap.T,
    origin="lower",
    extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
    cmap="YlOrRd",
    norm=LogNorm()
)

plt.colorbar(label="Complaint Density (log scale)")
plt.title("Spatial Density of Noise Complaints", fontsize=14, fontweight="bold")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.tight_layout()
plt.savefig(output_dir / "heatmap_density.png", dpi=300)
plt.close()

# Nearest neighbor clustering analysis
print("\nComputing nearest-neighbor clustering...")
coords = df[["Longitude", "Latitude"]].dropna().values
sample_n = min(1500, len(coords))
avg_distances = []

for i in range(sample_n):
    d = distance.cdist([coords[i]], coords)[0]
    d_sorted = np.sort(d)[1:6]
    avg_distances.append(d_sorted.mean())

# Histogram of nearest neighbor distances
plt.figure(figsize=(8, 5))
sns.histplot(avg_distances, bins=30, kde=True, color="purple")
plt.title("Spatial Clustering (Nearest Neighbor Distance)", fontsize=14, fontweight="bold")
plt.xlabel("Avg. Distance to 5 Nearest Neighbors")
plt.ylabel("Frequency")

plt.tight_layout()
plt.savefig(output_dir / "nnd_distribution.png", dpi=300)
plt.close()

# Temporal trend analysis
print("\nAnalyzing temporal trends...")
df["Created Date"] = pd.to_datetime(df["Created Date"], errors="coerce")
time_df = df.dropna(subset=["Created Date"]).copy()

# Hour-of-day trend
time_df["Hour"] = time_df["Created Date"].dt.hour
hour_counts = time_df.groupby("Hour").size().reindex(range(24), fill_value=0)

plt.figure(figsize=(10, 5))
sns.lineplot(x=hour_counts.index, y=hour_counts.values, marker="o", color="teal")
plt.title("Noise Complaints by Hour of Day", fontsize=14, fontweight="bold")
plt.xlabel("Hour of Day (0-23)")
plt.ylabel("Number of Complaints")
plt.xticks(range(0, 24, 2))
plt.grid(alpha=0.25)
plt.tight_layout()
plt.savefig(output_dir / "hourly_trend.png", dpi=300)
plt.close()

# Day-of-week trend
weekday_order = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]
time_df["Weekday"] = pd.Categorical(
    time_df["Created Date"].dt.day_name(),
    categories=weekday_order,
    ordered=True
)
weekday_counts = time_df.groupby("Weekday", observed=False).size().reindex(
    weekday_order,
    fill_value=0
)

plt.figure(figsize=(10, 5))
sns.barplot(x=weekday_counts.index, y=weekday_counts.values, hue=weekday_counts.index, palette="mako", legend=False)
plt.title("Noise Complaints by Day of Week", fontsize=14, fontweight="bold")
plt.xlabel("Day of Week")
plt.ylabel("Number of Complaints")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(output_dir / "weekly_trend.png", dpi=300)
plt.close()

print("\nAll analysis complete. Figures saved to:", output_dir)

