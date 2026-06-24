import requests
import re

PATH_README = "README.md"

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
        "soil_temperature_0_to_10cm,visibility"
    )

    data = requests.get(url, timeout=30).json()
    current = data["current"]

    temp = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    code = current["weather_code"]
    wind = current["wind_speed_10m"]
    uv = current["uv_index"]
    is_day = current["is_day"]
    soil = current["soil_temperature_0_to_10cm"]
    visibility = current["visibility"]

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
        95: "⛈️ Thunderstorm"
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

    # Wind
    if wind > 30:
        wind_text = "🌪️ Strong wind (tornado jir!)"
    elif wind > 15:
        wind_text = "💨 Breezy"
    else:
        wind_text = "🍃 Calm"

    return temp, humidity, desc, wind, uv_text, day_state, soil, vis_text


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


def main():
    temp, humidity, desc, wind, uv_text, day_state, soil, vis_text = get_weather()

    block = f"""{START_MARKER}
<div align="center">

### 🌦️ Weather in Me
<h3>(Updated Approximately Every 2 to 3 Hour)</h3>

**{desc}**

🌡️ Temperature: {temp}°C  
💧 Humidity: {humidity}%  
💨 Wind: {wind} km/h  
☀️ UV: {uv_text}  
🌗 Time: {day_state}  
🌱 Soil Temp (10cm): {soil}°C  
👀 Visibility: {vis_text}

</div>
{END_MARKER}"""

    update_readme(block)

    print("Weather updated!")


if __name__ == "__main__":
    main()
