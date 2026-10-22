"""
build_real_dataset.py
=====================
Builds an extensive, diverse training dataset by fetching actual historical 
daily weather from Open-Meteo ERA5 Archive API (100% free, real observed data).

Covers:
  1. Major Indian Monsoon & Flash Floods (Kerala, Assam, Bihar, Mumbai, Gujarat, Himachal, Chennai, etc.)
  2. Diverse Global Floods across All Climates (Tropical, Temperate, Mediterranean, Arid Flash Floods, Snowmelt)
  3. Moderate Heavy Rain days (non-catastrophic rains, 10-35mm)
  4. Diverse Safe/Dry/Mild Weather Periods across different seasons & terrains
"""

import requests
import pandas as pd
import time
import sys

# ──────────────────────────────────────────────────────────────
# 1. REAL HISTORICAL FLOOD EVENTS (Rain-induced floods & flash floods)
# ──────────────────────────────────────────────────────────────
FLOOD_EVENTS = [
    # ── India Floods & Cloudbursts ──
    {"name": "Kerala Aug 2018 Flood",        "lat":  9.94, "lon": 76.27, "start": "2018-08-08", "end": "2018-08-19"},
    {"name": "Kerala Aug 2019 Wayanad",       "lat": 11.68, "lon": 76.13, "start": "2019-08-07", "end": "2019-08-14"},
    {"name": "Mumbai July 2019 Deluge",       "lat": 19.07, "lon": 72.88, "start": "2019-07-01", "end": "2019-07-05"},
    {"name": "Mumbai July 2021 Flood",        "lat": 19.07, "lon": 72.88, "start": "2021-07-16", "end": "2021-07-22"},
    {"name": "Chiplun/Mahad July 2021",       "lat": 17.53, "lon": 73.51, "start": "2021-07-21", "end": "2021-07-24"},
    {"name": "Assam Brahmaputra Jun 2022",    "lat": 26.14, "lon": 91.73, "start": "2022-06-13", "end": "2022-06-22"},
    {"name": "Assam Silchar Floods 2022",     "lat": 24.83, "lon": 92.77, "start": "2022-06-18", "end": "2022-06-26"},
    {"name": "Bihar Kosi Floods Jul 2020",    "lat": 25.59, "lon": 85.13, "start": "2020-07-15", "end": "2020-07-25"},
    {"name": "Himachal Kullu/Mandi Jul 2023", "lat": 31.95, "lon": 77.10, "start": "2023-07-08", "end": "2023-07-13"},
    {"name": "Himachal Mandi Aug 2023",       "lat": 31.70, "lon": 76.93, "start": "2023-08-12", "end": "2023-08-16"},
    {"name": "Uttarakhand Cloudburst Oct 2021","lat": 29.39, "lon": 79.45, "start": "2021-10-17", "end": "2021-10-21"},
    {"name": "Chennai Cyclone Michaung 2023", "lat": 13.08, "lon": 80.27, "start": "2023-12-03", "end": "2023-12-06"},
    {"name": "Chennai Nov 2021 Floods",       "lat": 13.08, "lon": 80.27, "start": "2021-11-06", "end": "2021-11-12"},
    {"name": "Gujarat Vadodara Aug 2024",     "lat": 22.30, "lon": 73.18, "start": "2024-08-25", "end": "2024-08-30"},
    {"name": "Gujarat Surat Flood 2019",      "lat": 21.17, "lon": 72.83, "start": "2019-08-08", "end": "2019-08-14"},
    {"name": "Hyderabad Deluge Oct 2020",     "lat": 17.38, "lon": 78.48, "start": "2020-10-12", "end": "2020-10-16"},
    {"name": "Bengaluru Deluge Sep 2022",     "lat": 12.97, "lon": 77.59, "start": "2022-09-04", "end": "2022-09-08"},
    {"name": "Odisha Cyclone Fani/Rain 2019", "lat": 20.29, "lon": 85.82, "start": "2019-05-02", "end": "2019-05-05"},
    {"name": "Delhi Yamuna Floods Jul 2023",  "lat": 28.61, "lon": 77.20, "start": "2023-07-08", "end": "2023-07-13"},
    {"name": "Sikkim Teesta Flash Flood 2023","lat": 27.53, "lon": 88.51, "start": "2023-10-03", "end": "2023-10-06"},

    # ── Global Major Floods across Continents ──
    {"name": "Pakistan Sindh Megafloods 2022","lat": 27.03, "lon": 68.32, "start": "2022-08-18", "end": "2022-08-31"},
    {"name": "Bangladesh Sylhet Jun 2022",    "lat": 24.90, "lon": 91.87, "start": "2022-06-15", "end": "2022-06-23"},
    {"name": "Nepal Kathmandu Sep 2024",      "lat": 27.72, "lon": 85.32, "start": "2024-09-26", "end": "2024-09-29"},
    {"name": "Germany/Belgium Ahr Valley 2021","lat": 50.35,"lon":  6.95, "start": "2021-07-13", "end": "2021-07-17"},
    {"name": "Bavaria Germany Jun 2024",      "lat": 48.13, "lon": 11.58, "start": "2024-05-31", "end": "2024-06-04"},
    {"name": "Italy Emilia-Romagna 2023",     "lat": 44.49, "lon": 11.34, "start": "2023-05-15", "end": "2023-05-19"},
    {"name": "Greece Storm Daniel 2023",      "lat": 39.64, "lon": 22.42, "start": "2023-09-04", "end": "2023-09-08"},
    {"name": "Slovenia Floods Aug 2023",      "lat": 46.05, "lon": 14.50, "start": "2023-08-03", "end": "2023-08-06"},
    {"name": "Libya Derna Storm Daniel 2023", "lat": 32.76, "lon": 22.64, "start": "2023-09-09", "end": "2023-09-12"},
    {"name": "China Henan Zhengzhou Jul 2021","lat": 34.76, "lon": 113.66,"start": "2021-07-19", "end": "2021-07-22"},
    {"name": "Japan Kyushu Floods Jul 2020",   "lat": 32.75, "lon": 130.74,"start": "2020-07-03", "end": "2020-07-07"},
    {"name": "South Korea Seoul Aug 2022",    "lat": 37.57, "lon": 126.98,"start": "2022-08-08", "end": "2022-08-11"},
    {"name": "Philippines Typhoon Rai 2021",  "lat": 10.31, "lon": 123.89,"start": "2021-12-15", "end": "2021-12-18"},
    {"name": "Vietnam Central Floods 2020",   "lat": 16.46, "lon": 107.59,"start": "2020-10-11", "end": "2020-10-18"},
    {"name": "Dubai/UAE Historic Deluge 2024","lat": 25.20, "lon": 55.27, "start": "2024-04-15", "end": "2024-04-17"},
    {"name": "USA Kentucky Floods Jul 2022",  "lat": 37.26, "lon": -82.93,"start": "2022-07-27", "end": "2022-07-30"},
    {"name": "USA Vermont Floods Jul 2023",   "lat": 44.26, "lon": -72.58,"start": "2023-07-09", "end": "2023-07-12"},
    {"name": "Brazil Petropolis Feb 2022",    "lat": -22.51,"lon": -43.18,"start": "2022-02-14", "end": "2022-02-17"},
    {"name": "Brazil Rio Grande do Sul 2024", "lat": -30.03,"lon": -51.23,"start": "2024-04-28", "end": "2024-05-06"},
    {"name": "South Africa Durban Apr 2022",  "lat": -29.85,"lon": 30.98, "start": "2022-04-10", "end": "2022-04-13"},
    {"name": "Australia Queensland Feb 2022", "lat": -27.47,"lon": 153.03,"start": "2022-02-25", "end": "2022-03-01"},
]

# ──────────────────────────────────────────────────────────────
# 2. DIVERSE SAFE/NORMAL PERIODS (Dry, pleasant, seasonal, hot, cold)
# ──────────────────────────────────────────────────────────────
SAFE_PERIODS = [
    # Indian Cities across different safe months
    {"name": "Mumbai dry winter",         "lat": 19.07, "lon": 72.88, "start": "2023-01-10", "end": "2023-01-30"},
    {"name": "Pune sunny spring",         "lat": 18.52, "lon": 73.85, "start": "2023-03-01", "end": "2023-03-25"},
    {"name": "Delhi dry autumn",          "lat": 28.61, "lon": 77.20, "start": "2023-10-15", "end": "2023-11-05"},
    {"name": "Bengaluru pleasant winter", "lat": 12.97, "lon": 77.59, "start": "2023-01-01", "end": "2023-01-20"},
    {"name": "Kolkata dry winter",        "lat": 22.57, "lon": 88.36, "start": "2023-01-05", "end": "2023-01-25"},
    {"name": "Chennai dry summer",        "lat": 13.08, "lon": 80.27, "start": "2023-05-01", "end": "2023-05-20"},
    {"name": "Ahmedabad dry hot summer",  "lat": 23.02, "lon": 72.57, "start": "2023-04-01", "end": "2023-04-20"},
    {"name": "Jaipur arid dry season",    "lat": 26.91, "lon": 75.78, "start": "2023-02-01", "end": "2023-02-25"},
    {"name": "Shimla cool clear autumn",  "lat": 31.10, "lon": 77.17, "start": "2023-10-01", "end": "2023-10-20"},
    {"name": "Bhubaneswar dry winter",    "lat": 20.29, "lon": 85.82, "start": "2023-01-01", "end": "2023-01-20"},
    {"name": "Guwahati dry winter",       "lat": 26.14, "lon": 91.73, "start": "2023-01-10", "end": "2023-01-28"},
    {"name": "Kochi fair weather",        "lat":  9.93, "lon": 76.26, "start": "2023-02-01", "end": "2023-02-20"},
    {"name": "Lucknow clear winter",      "lat": 26.84, "lon": 80.94, "start": "2023-11-01", "end": "2023-11-20"},
    {"name": "Nagpur pleasant winter",    "lat": 21.14, "lon": 79.08, "start": "2023-12-01", "end": "2023-12-20"},

    # Global Diverse Climates (Arid, Continental, Mediterranean, Oceanic)
    {"name": "London spring calm",        "lat": 51.51, "lon": -0.13, "start": "2023-04-15", "end": "2023-05-10"},
    {"name": "Paris summer dry",          "lat": 48.85, "lon":  2.35, "start": "2023-07-01", "end": "2023-07-20"},
    {"name": "Munich autumn calm",        "lat": 48.13, "lon": 11.58, "start": "2023-09-15", "end": "2023-10-05"},
    {"name": "Rome sunny summer",         "lat": 41.90, "lon": 12.50, "start": "2023-07-01", "end": "2023-07-25"},
    {"name": "Athens Mediterranean dry",  "lat": 37.98, "lon": 23.73, "start": "2023-08-01", "end": "2023-08-25"},
    {"name": "Cairo desert dry",          "lat": 30.04, "lon": 31.24, "start": "2023-04-01", "end": "2023-04-30"},
    {"name": "Dubai arid calm",           "lat": 25.20, "lon": 55.27, "start": "2023-01-01", "end": "2023-01-25"},
    {"name": "Tokyo clear spring",        "lat": 35.68, "lon": 139.69,"start": "2023-04-01", "end": "2023-04-20"},
    {"name": "Sydney sunny spring",       "lat": -33.87,"lon": 151.21,"start": "2023-09-01", "end": "2023-09-20"},
    {"name": "New York clear autumn",     "lat": 40.71, "lon": -74.01,"start": "2023-10-01", "end": "2023-10-25"},
    {"name": "Los Angeles dry summer",    "lat": 34.05, "lon": -118.24,"start":"2023-06-01", "end": "2023-06-30"},
    {"name": "Buenos Aires spring",       "lat": -34.61,"lon": -58.38,"start": "2023-10-01", "end": "2023-10-20"},
    {"name": "Cape Town dry summer",      "lat": -33.93,"lon": 18.42, "start": "2023-01-01", "end": "2023-01-25"},
    {"name": "Nairobi pleasant season",   "lat": -1.29, "lon": 36.82, "start": "2023-07-01", "end": "2023-07-25"},
]

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

def fetch_weather(lat, lon, start, end):
    """Fetch daily weather from Open-Meteo historical archive."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
            "cloudcover_mean",
            "relative_humidity_2m_max",
        ]),
        "timezone": "auto",
    }
    try:
        r = requests.get(ARCHIVE_URL, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        d = data["daily"]
        records = []
        for i, date in enumerate(d["time"]):
            temp_max = d["temperature_2m_max"][i]
            temp_min = d["temperature_2m_min"][i]
            precip = d["precipitation_sum"][i]
            if temp_max is None or temp_min is None or precip is None:
                continue
            records.append({
                "Temperature":   round((temp_max + temp_min) / 2, 2),
                "Max_Temp":      round(temp_max, 2),
                "Windspeed":     round(d["windspeed_10m_max"][i] or 0, 2),
                "Cloud_Cover":   round(d["cloudcover_mean"][i] or 0, 2),
                "Precipitation": round(precip, 2),
                "Humidity":      round(d["relative_humidity_2m_max"][i] or 0, 2),
            })
        return records
    except Exception as e:
        print(f"  WARNING: API error for {lat},{lon}: {e}")
        return []

rows = []

print("Fetching extensive FLOOD event weather data...")
for ev in FLOOD_EVENTS:
    print(f"  {ev['name']}...", end=" ", flush=True)
    records = fetch_weather(ev["lat"], ev["lon"], ev["start"], ev["end"])
    # Only keep days with genuine flood-producing rain (>= 15mm)
    valid_count = 0
    for r in records:
        if r["Precipitation"] >= 15.0:
            r["Flood"] = 1
            rows.append(r)
            valid_count += 1
    print(f"{valid_count} flood days")
    time.sleep(0.2)

print("\nFetching extensive SAFE period weather data...")
for ev in SAFE_PERIODS:
    print(f"  {ev['name']}...", end=" ", flush=True)
    records = fetch_weather(ev["lat"], ev["lon"], ev["start"], ev["end"])
    for r in records:
        r["Flood"] = 0
        rows.append(r)
    print(f"{len(records)} safe days")
    time.sleep(0.2)

df = pd.DataFrame(rows)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nTotal records collected: {len(df)}")
print("Label distribution:")
print(df["Flood"].value_counts())
print("\nWeather ranges:")
for col in ["Temperature", "Max_Temp", "Windspeed", "Cloud_Cover", "Precipitation", "Humidity"]:
    print(f"  {col}: {df[col].min():.1f} - {df[col].max():.1f}")

df.to_csv("flood_training_data.csv", index=False)
print("\nSaved to flood_training_data.csv")
