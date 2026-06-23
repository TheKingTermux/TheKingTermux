import requests
import re

PATH_README = "README.md"

START_MARKER = "<!-- START_SECTION:weather -->"
END_MARKER = "<!-- END_SECTION:weather -->"

LAT = -7.931080
LON = 112.660860


def get_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}"
        f"&longitude={LON}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code"
    )

    data = requests.get(url, timeout=30).json()

    current = data["current"]

    temp = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    code = current["weather_code"]

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

    return temp, humidity, desc


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
    temp, humidity, desc = get_weather()

    block = f"""{START_MARKER}
    <div align="center">
### 🌦️ Weather in Me

> {desc}
>
> 🌡️ Temperature: {temp}°C
>
> 💧 Humidity: {humidity}%
    </div>
{END_MARKER}"""

    update_readme(block)

    print("Weather updated!")


if __name__ == "__main__":
    main()
