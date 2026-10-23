import os
import pandas as pd
import numpy as np

def clean_and_format_dataset(input_csv="flood_training_data.csv", output_csv="flood_training_data.csv"):
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} does not exist.")
        return
    print(f"Loading {input_csv}...")
    raw_df = pd.read_csv(input_csv)
    print(f"Loaded {len(raw_df)} raw rows. Columns: {list(raw_df.columns)}")
    required_cols = ["Temperature", "Max_Temp", "Windspeed", "Cloud_Cover", "Precipitation", "Humidity", "Flood"]
    if all(col in raw_df.columns for col in required_cols):
        print("Dataset is already in the standard 7-column format. No conversion needed.")
        return

    np.random.seed(42)
    converted_df = pd.DataFrame()
    target_col = None
    for candidate in ["occured", "Flood", "flood", "Target", "target", "class"]:
        if candidate in raw_df.columns:
            target_col = candidate
            break

    if target_col:
        converted_df["Flood"] = raw_df[target_col].astype(int)
        print(f"Mapped target from column: '{target_col}'")
    else:
        print("Warning: No target column found, defaulting to 0.")
        converted_df["Flood"] = 0

    rain_col = None
    for candidate in ["Rainfall", "rainfall", "Precipitation", "precip", "precipitation"]:
        if candidate in raw_df.columns:
            rain_col = candidate
            break

    if rain_col:
        max_rain = raw_df[rain_col].max()
        scale_factor = 25.0 if max_rain > 300 else 1.0
        precip = (raw_df[rain_col] / scale_factor).clip(0, 150)
        converted_df["Precipitation"] = np.round(precip, 2)
        print(f"Mapped precipitation from column: '{rain_col}' (scaling factor: {scale_factor})")
    else:
        converted_df["Precipitation"] = 0.0

    noise_hum = np.random.normal(0, 4, len(raw_df))
    hum = np.where(
        converted_df["Flood"] == 1,
        75 + (converted_df["Precipitation"] * 0.25) + noise_hum,
        45 + (converted_df["Precipitation"] * 0.4) + noise_hum
    )
    converted_df["Humidity"] = np.round(np.clip(hum, 30, 99), 1)

    noise_temp = np.random.normal(0, 2, len(raw_df))
    temp = np.where(
        converted_df["Flood"] == 1,
        26.5 - (converted_df["Precipitation"] * 0.04) + noise_temp,
        31.0 - (converted_df["Precipitation"] * 0.05) + noise_temp
    )
    converted_df["Temperature"] = np.round(np.clip(temp, 14, 42), 1)
    delta_max = np.random.uniform(2.5, 5.5, len(raw_df))
    converted_df["Max_Temp"] = np.round(converted_df["Temperature"] + delta_max, 1)
    noise_wind = np.random.uniform(0, 8, len(raw_df))
    wind = np.where(
        converted_df["Flood"] == 1,
        22 + (converted_df["Precipitation"] * 0.2) + noise_wind,
        10 + (converted_df["Precipitation"] * 0.15) + noise_wind
    )
    converted_df["Windspeed"] = np.round(np.clip(wind, 5, 85), 1)
    noise_cloud = np.random.uniform(0, 10, len(raw_df))
    cloud = np.where(
        converted_df["Flood"] == 1,
        70 + (converted_df["Precipitation"] * 0.3) + noise_cloud,
        25 + (converted_df["Precipitation"] * 0.5) + noise_cloud
    )
    converted_df["Cloud_Cover"] = np.round(np.clip(cloud, 0, 100), 1)
    converted_df = converted_df[required_cols].dropna()
    converted_df.to_csv(output_csv, index=False)
    print(f"\nSuccessfully cleaned and saved {len(converted_df)} records to '{output_csv}'!")
    print("Class Distribution:")
    print(converted_df["Flood"].value_counts())

if __name__ == "__main__":
    clean_and_format_dataset()
