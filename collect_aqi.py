import requests
import pandas as pd
import datetime
import os

# ✅ API Keys
AQICN_TOKEN = "2eb7e59a27fec6826892da8d9b3f9ff95e6c573e"
OPENWEATHER_KEY = "ee88310481e99a7843bdedc0cca27fd1"

# ✅ Location
CITY = "karachi"
COUNTRY = "PK"

# ✅ AQICN Data Fetch
def get_aqi_and_pollutants():
    try:
        url = f"https://api.waqi.info/feed/{CITY}/?token={AQICN_TOKEN}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "ok":
            return None
        iaqi = data["data"].get("iaqi", {})
        return {
            "aqi": data["data"].get("aqi"),
            "pm25": iaqi.get("pm25", {}).get("v"),
            "pm10": iaqi.get("pm10", {}).get("v"),
            "co": iaqi.get("co", {}).get("v"),
            "no2": iaqi.get("no2", {}).get("v"),
            "o3": iaqi.get("o3", {}).get("v"),
            "so2": iaqi.get("so2", {}).get("v")
        }
    except Exception as e:
        print("AQI Error:", e)
        return None

# ✅ OpenWeather Data Fetch
def get_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY}&appid={OPENWEATHER_KEY}&units=metric"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        if "main" not in data or "wind" not in data:
            return None
        return {
            "temp": data["main"].get("temp"),
            "humidity": data["main"].get("humidity"),
            "pressure": data["main"].get("pressure"),
            "wind_speed": data["wind"].get("speed")
        }
    except Exception as e:
        print("Weather Error:", e)
        return None

# ✅ Collect and Log Hourly Data
def collect_one_hour():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    hour = now.hour + 1  # Convert 0–23 to 1–24

    folder_path = f"data/{date_str}"
    os.makedirs(folder_path, exist_ok=True)
    csv_path = os.path.join(folder_path, "karachi.csv")

    aqi = get_aqi_and_pollutants()
    weather = get_weather()

    if aqi is None or weather is None:
        print("❌ Data not available")
        return

    row = {
        "date": date_str,
        "time": time_str,
        "hour": hour,
        **aqi,
        **weather
    }

    df = pd.DataFrame([row])

    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)

    print(f"✅ Logged hour {hour}:00 → {csv_path}")

# ✅ Main
if __name__ == "__main__":
    collect_one_hour()


