import requests
import re
import json
import os
from datetime import datetime

PATH_README = "README.md"
PATH_STATUS = "status.json"

START_MARKER = "<!-- START_SECTION:weather -->"
END_MARKER = "<!-- END_SECTION:weather -->"

LAT = -7.931080
LON = 112.660860


def get_weather():
    url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}"
    f"&longitude={LON}"
    "&current=temperature_2m,relative_humidity_2m,weather_code,"
    "wind_speed_10m,uv_index,is_day,"
    "soil_temperature_0_to_10cm,visibility,"
    "cloud_cover,precipitation"
    "&daily=sunrise,sunset,precipitation_hours"
    "&hourly=visibility"
    "&timezone=Asia%2FBangkok"
    )

    data = requests.get(url, timeout=30).json()
    current = data["current"]
    daily = data["daily"]
    hourly = data["hourly"]

    temp = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    code = current["weather_code"]
    wind = current["wind_speed_10m"]
    uv = current["uv_index"]
    is_day = current["is_day"]
    soil = current["soil_temperature_0_to_10cm"]
    visibility = current["visibility"]
    cloud_cover = current["cloud_cover"]
    precipitation = current["precipitation"]
    sunrise = daily["sunrise"][0][-5:]
    sunset = daily["sunset"][0][-5:]
    rain_hours = daily["precipitation_hours"][0]

    weather_map = {
        0: "☀️ Clear Sky",
        1: "🌤️ Mainly Clear",
        2: "⛅ Partly Cloudy",
        3: "☁️ Overcast",
        45: "🌫️ Fog",
        48: "🌫️ Fog",
        51: "🌦️ Light Drizzle",
        61: "🌧️ Rain",
        63: "🌧️ Moderate Rain",
        65: "⛈️ Heavy Rain",
        80: "🌦️ Rain Showers",
        95: "⛈️ Thunderstorm (awas kilat!)"
    }

    desc = weather_map.get(code, "🌍 Unknown")
    day_state = "🌞 Day" if is_day == 1 else "🌙 Night"

    # UV
    if uv >= 8:
        uv_text = "☠️ Extreme UV (pakai sunscreen bro!)"
    elif uv >= 5:
        uv_text = "⚠️ High UV"
    else:
        uv_text = "🟢 Safe UV"

    # Visibility
    if visibility >= 10000:
        vis_text = "Excellent"
    elif visibility >= 5000:
        vis_text = "Good"
    else:
        vis_text = "Poor"

    today = daily["sunrise"][0][:10]

    today_vis = [
        vis
        for t, vis in zip(hourly["time"], hourly["visibility"])
        if t.startswith(today)
    ]

    if today_vis:
        min_visibility = min(today_vis)
        max_visibility = max(today_vis)
    else:
        min_visibility = visibility
        max_visibility = visibility

    # Wind
    if wind > 30:
        wind_text = "🌪️ Strong wind (tornado jir!)"
    elif wind > 15:
        wind_text = "💨 Breezy"
    else:
        wind_text = "🍃 Calm"

    return (
        temp,
        humidity,
        desc,
        wind,
        wind_text,
        uv_text,
        day_state,
        soil,
        vis_text,
        cloud_cover,
        precipitation,
        sunrise,
        sunset,
        rain_hours,
        visibility,
        min_visibility,
        max_visibility
    )

def update_readme(block):
    with open(PATH_README, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL
    )

    content = pattern.sub(block, content)

    with open(PATH_README, "w", encoding="utf-8") as f:
        f.write(content)

def load_status():
    if os.path.exists(PATH_STATUS):
        with open(PATH_STATUS, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def save_status(status):
    with open(PATH_STATUS, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)


def update_weather_tracker():
    status = load_status()

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    previous_time = status.get("weather_last_update")

    compare_text = "First Run"

    if previous_time:
        try:
            old = datetime.strptime(
                previous_time,
                "%Y-%m-%d %H:%M:%S"
            )

            diff = now - old

            total = int(diff.total_seconds())

            h = total // 3600
            m = (total % 3600) // 60
            s = total % 60

            compare_text = f"{h:02d}:{m:02d}:{s:02d}"

        except Exception:
            compare_text = "Unknown"

    status["weather_last_update"] = current_time
    status["weather_compare"] = compare_text

    save_status(status)

    return current_time, compare_text

def main():
    (
        temp,
        humidity,
        desc,
        wind,
        wind_text,
        uv_text,
        day_state,
        soil,
        vis_text,
        cloud_cover,
        precipitation,
        sunrise,
        sunset,
        rain_hours,
        visibility,
        min_visibility,
        max_visibility
    ) = get_weather()
    last_update, compare_time = update_weather_tracker()

    block = f"""{START_MARKER}
<div align="center">

### 🌦️ Weather in Me
##### (Updated Approximately Every 2 to 3 Hour)
##### 🕒 Last Updated: {last_update}
##### ⏱️ Since Previous Update: {compare_time}

**{desc}**

🌡️ Temperature: {temp}°C  
💧 Humidity: {humidity}%  
🌱 Soil Temp: {soil}°C

☁️ Cloud Cover: {cloud_cover}%  
☔ Precipitation: {precipitation} mm  
🌧️ Rain Hours: {rain_hours} h

💨 Wind Speed: {wind} km/h ({wind_text})

☀️ UV: {uv_text}  
🌗 Time: {day_state}

🌅 Sunrise: {sunrise}  
🌇 Sunset: {sunset}

👀 Visibility: {visibility} m  ({vis_text})

🔻 Min: {min_visibility} m  
🔺 Max: {max_visibility} m

</div>
{END_MARKER}"""

    update_readme(block)

    print("Weather updated!")

if __name__ == "__main__":
    main()
