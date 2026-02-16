# NYC Noise Pollution Analysis

This project analyzes NYC 311 noise complaints with a focus on data quality, spatial patterns, and temporal trends. It is designed as a data analysis project for urban decision support.

## Key Findings (Quantified)

The following results come from the latest run on `2025-12-04` dataset snapshot after cleaning (`763,779` records):

1. Manhattan has the highest complaint density at about `2,889` complaints per sq km, followed by Bronx (`2,244`), despite Bronx having the largest raw complaint count.
2. Bronx has the largest complaint volume (`245,284`), while Staten Island is much lower (`16,688`), showing strong cross-borough imbalance.
3. Borough-level complaint distribution differs significantly under a chi-square test (`chi2 = 187,809.8`, greater than critical value `9.49`), indicating non-uniform spatial concentration.

## Data Source

- Primary source: [NYC Open Data - 311 Service Requests Updates](https://opendata.cityofnewyork.us/311-service-requests-from-2010-to-present-updates/) (official)
- Dataset context (Dec 2025 update): the platform notes naming updates (`Complaint Type` / `Descriptor` display labels) and a split into separate time-range datasets to improve usability.
- This project uses noise-related records from the 311 export.
- Input file used by the scripts: `Data/data.csv`
- Current raw file in this repo: `data/Data/311_Service_Requests_from_2010_to_Present_20251204.csv`

If your raw filename differs, map or copy it to `Data/data.csv` before running.

## Project Structure

- `code/clean.py`: data cleaning pipeline
- `code/Analysis.py`: statistical, spatial, and temporal analysis + figure generation
- `cleanData/noise_complaints_clean.csv`: cleaned output
- `output/`: generated plots

## Cleaning Rules

`code/clean.py` applies the following logic:

1. Keep only rows where `Complaint Type` contains `noise` (case-insensitive).
2. Normalize `Borough` text (`strip`, title case), remove invalid values (`Unspecified`, empty, etc.).
3. Validate coordinates against NYC bounds:
   - Latitude: `40.477` to `40.917`
   - Longitude: `-74.259` to `-73.700`
4. Round coordinates to 6 decimals.
5. Remove duplicates and drop rows with missing critical fields:
   - `Borough`, `Latitude`, `Longitude`, `Descriptor`

## Analysis Methods

`code/Analysis.py` includes:

- Borough complaint counts and complaint density (count per sq km)
- Top descriptor analysis by borough (stacked bar chart)
- Chi-square goodness-of-fit style test for borough distribution
- Spatial scatter map and 2D log-scaled density heatmap
- Nearest-neighbor clustering proxy (average distance to 5 nearest neighbors, sampled up to 1500 points)
- Temporal trends:
  - complaints by hour of day
  - complaints by day of week

## Output Figures

Running the full pipeline generates:

- `output/borough_counts.png`
- `output/borough_density.png`
- `output/borough_descriptor.png`
- `output/chi_square_observed.png`
- `output/scatter_map.png`
- `output/heatmap_density.png`
- `output/nnd_distribution.png`
- `output/hourly_trend.png`
- `output/weekly_trend.png`

## Reproducibility

### 1) Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 2) Run cleaning

```bash
python code/clean.py
```

### 3) Run analysis and generate plots

```bash
python code/Analysis.py
```

## Limitations

1. 311 complaints are report-based and may reflect reporting behavior bias, not only real noise intensity.
2. The chi-square setup in this version compares observed borough counts against equal expected counts; domain-aware baselines (population or exposure adjusted) would be stronger.
3. Nearest-neighbor distance is computed in lat/lon coordinate space, not projected meter-based distance.
4. This is a cross-sectional analysis snapshot and does not model long-term causal drivers.

## Interview Framing (How to Present This Project)

When discussing this project in interviews, focus on:

1. Why these cleaning rules:
   - urban geospatial analysis is very sensitive to coordinate quality and category consistency.
2. Why these metrics:
   - count captures demand volume, density captures intensity, and both are needed for fair borough comparison.
3. Decision relevance:
   - results can guide where city teams prioritize enforcement, outreach, or mitigation resources.
4. Method awareness:
   - clearly state assumptions and bias risks, then propose next-step improvements (population-normalized rates, projected distances, seasonal decomposition).
