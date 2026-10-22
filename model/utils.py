import os
import requests
import joblib
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", message="X does not have valid feature names")

API_KEY = os.getenv("VISUAL_CROSSING_API_KEY", "VY7NZSTK366CHHKPN8U6EJEM5")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "flood_model.pkl")

xgb_model = None
rf_model = None
logistic_poly = None
scaler = None

try:
    model_package = joblib.load(MODEL_PATH)

    xgb_model = model_package["xgb_model"]
    rf_model = model_package["rf_model"]
    logistic_poly = model_package["logistic_poly"]
    scaler = model_package["scaler"]
except Exception as e:
    print(f"Error loading models: {e}")


def _format_resolved_location(resolved_address, raw_city):
    """Ensure resolved location always shows City, State, Country when available."""
    if resolved_address and "," in resolved_address:
        return resolved_address

    lookup_name = resolved_address or raw_city
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(lookup_name)}&count=1&language=en&format=json"
        res = requests.get(url, timeout=3).json().get("results", [])
        if res:
            item = res[0]
            name = item.get("name")
            admin1 = item.get("admin1")
            country = item.get("country")
            parts = []
            if name:
                parts.append(name)
            if admin1 and admin1.lower() != name.lower():
                parts.append(admin1)
            if country:
                parts.append(country)
            if len(parts) >= 2:
                return ", ".join(parts)
    except Exception:
        pass

    return (resolved_address or raw_city).title()

def get_city_weather(city):
    url = (
        "https://weather.visualcrossing.com/"
        "VisualCrossingWebServices/rest/services/timeline/"
        f"{requests.utils.quote(city)}"
    )

    params = {
        "unitGroup": "metric",
        "key": API_KEY,
        "include": "current"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        current = data["currentConditions"]
        today = data["days"][0]

        return {
            "city": _format_resolved_location(data.get("resolvedAddress"), city),
            "temp": current["temp"],
            "cloud": current["cloudcover"],
            "max_temp": today["tempmax"],
            "precip": today["precip"],
            "wind": current["windspeed"],
            "humidity": current["humidity"]
        }

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Weather API request failed: {e}")

    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise ValueError(f"Invalid weather data received: {e}")


def predict_flood(weather_data):
    if any(
        model is None
        for model in (xgb_model, rf_model, logistic_poly, scaler)
    ):
        raise RuntimeError(
            "Flood prediction models are not loaded. "
            "Check model/flood_model.pkl and its contents."
        )

    features = np.array([
        weather_data["temp"],
        weather_data["max_temp"],
        weather_data["wind"],
        weather_data["cloud"],
        weather_data["precip"],
        weather_data["humidity"]
    ], dtype=float).reshape(1, -1)

    features_scaled = scaler.transform(features)

    xgb_prob = xgb_model.predict_proba(features_scaled)[0][1]
    rf_prob = rf_model.predict_proba(features_scaled)[0][1]
    logistic_prob = logistic_poly.predict_proba(features_scaled)[0][1]

    ensemble_prob = (
        xgb_prob * 0.4
        + rf_prob * 0.4
        + logistic_prob * 0.2
    )

    # Physical meteorology safety check:
    # A flood cannot happen without significant rainfall. If precip is 0 or minimal (< 2mm),
    # clamp flood risk so dry, sunny, or mild weather never triggers false flood warnings.
    precip = weather_data.get("precip", 0.0)
    humidity = weather_data.get("humidity", 0.0)
    if precip <= 0.05:
        ensemble_prob = min(ensemble_prob, 0.08)
        xgb_prob = min(xgb_prob, 0.08)
        rf_prob = min(rf_prob, 0.08)
        logistic_prob = min(logistic_prob, 0.08)
    elif precip < 3.0 and humidity < 85:
        ensemble_prob = min(ensemble_prob, 0.20)
        xgb_prob = min(xgb_prob, 0.20)
        rf_prob = min(rf_prob, 0.20)
        logistic_prob = min(logistic_prob, 0.20)

    prediction_label = 1 if ensemble_prob > 0.5 else 0
    confidence = round(
        max(ensemble_prob, 1 - ensemble_prob) * 100, 2
    )

    label = "Unsafe" if prediction_label == 1 else "Safe"

    individual_probs = {
        "XGBoost": round(xgb_prob * 100, 1),
        "Random Forest": round(rf_prob * 100, 1),
        "Logistic Regression": round(logistic_prob * 100, 1)
    }

    return label, confidence, individual_probs
