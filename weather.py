import requests
import re
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

PATH_README = "README.md"
PATH_STATUS = "status.json"

START_MARKER = "<!-- START_SECTION:weather -->"
END_MARKER = "<!-- END_SECTION:weather -->"

lat_env = os.getenv("SECRET_LAT")
lon_env = os.getenv("SECRET_LON")

if lat_env is None or lon_env is None:
    raise ValueError("SECRET_LAT atau SECRET_LON belum di-set")

LAT = float(lat_env)
LON = float(lon_env)

def get_air_quality():
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={LAT}&longitude={LON}"
        "&current=pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,ozone,us_aqi"
    )

    data = requests.get(url, timeout=30).json()["current"]

    aqi = data.get("us_aqi") or 0

    if aqi >= 200:
        aqi_text = "☠️ Parah banget (ini udara atau racun cair?)"
    elif aqi >= 150:
        aqi_text = "😷 Tidak sehat (masker jangan cuma pajangan)"
    elif aqi >= 100:
        aqi_text = "😐 Kurang sehat (paru-paru kerja lembur)"
    elif aqi >= 50:
        aqi_text = "🙂 Sedang (masih oke tapi jangan sok bersih)"
    else:
        aqi_text = "😄 Bersih (hirup bebas, kayak hidup ideal)"

    return {
        "pm25": data.get("pm2_5", 0),
        "pm10": data.get("pm10", 0),
        "aqi": aqi,
        "aqi_text": aqi_text
    }

def get_weather():
    url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}"
    f"&longitude={LON}"
    "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m,uv_index,is_day,soil_temperature_0_to_10cm,visibility,cloud_cover,precipitation,apparent_temperature,pressure_msl,precipitation_probability"
    "&daily=sunrise,sunset,precipitation_hours"
    "&hourly=visibility,temperature_2m,weather_code,precipitation_probability,wind_speed_10m,uv_index,cloud_cover"
    "&timezone=Asia%2FBangkok"
    )

    data = requests.get(url, timeout=30).json()
    current = data["current"]
    daily = data["daily"]
    hourly = data["hourly"]

    forecast = []

    current_time = datetime.fromisoformat(current["time"])
    
    for i, t in enumerate(hourly["time"]):
        dt = datetime.fromisoformat(t)
    
        if dt >= current_time:
            forecast.append({
                "time": dt.strftime("%H:%M"),
                "code": hourly["weather_code"][i],
                "temp": hourly["temperature_2m"][i],
                "rain": hourly["precipitation_probability"][i],
                "wind": hourly["wind_speed_10m"][i],
                "cloud": hourly["cloud_cover"][i],
                "uv": hourly["uv_index"][i],
                "visibility": hourly["visibility"][i],
            })
    
        if len(forecast) == 5:
            break

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
    rain_chance = current.get("precipitation_probability", 0)
    feels_like = current["apparent_temperature"]
    wind_gust = current.get("wind_gusts_10m", 0)
    wind_dir = current.get("wind_direction_10m", 0)
    pressure = current.get("pressure_msl", 0)

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
    if uv >= 11:
        uv_text = "☠️ Extreme UV (matahari mode ngegas, jangan jadi sate manusia 🔥)"
    elif uv >= 8:
        uv_text = "🥵 Very High UV (kulit auto drama kalo lama di luar ☀️)"
    elif uv >= 5:
        uv_text = "⚠️ High UV (panasnya mulai toxic dikit)"
    elif uv >= 3:
        uv_text = "🟡 Moderate UV (masih aman tapi jangan sok kuat)"
    else:
        uv_text = "🟢 Safe UV (aman lah, kayak zona nyaman 😌)"

    # Visibility
    if visibility >= 20000:
        vis_text = "Excellent (anjir jernih banget, kayak mata elang 🦅)"
    elif visibility >= 10000:
        vis_text = "Very Good (lumayan bening, masih enak dipandang 👀)"
    elif visibility >= 5000:
        vis_text = "Good (masih oke lah, gak blur-blur amat)"
    elif visibility >= 2000:
        vis_text = "Moderate (agak gakelihatan, kayak mood Senin 😩)"
    else:
        vis_text = "Poor (tidor pun sodap ni 💤)"

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
    if wind > 40:
        wind_text = "🌪️ Extreme Storm (ini angin atau marahnya mantan?!)"
    elif wind > 30:
        wind_text = "🌪️ Strong Wind (pegangan bang, bisa mental dikit 😵‍💫)"
    elif wind > 15:
        wind_text = "💨 Breezy (enak sih, kayak kipas natural 😌)"
    elif wind > 5:
        wind_text = "🍃 Light Wind (cuma lewat doang, gak niat)"
    else:
        wind_text = "🍃 Calm (diam total, kayak WiFi pas ujian 😐)"

    # Wind Gust
    if wind_gust > 60:
        gust_text = "🌪️ Badai mini (atap bisa mikir kabur)"
    elif wind_gust > 40:
        gust_text = "💨 Kenceng banget (rambut auto gagal gaya)"
    elif wind_gust > 25:
        gust_text = "🍃 Lumayan nendang"
    else:
        gust_text = "😴 Tenang, angin lagi cuti"

    # Wind Direction
    def wind_direction_text(deg):
        dirs = ["Utara", "Timur Laut", "Timur", "Tenggara",
                "Selatan", "Barat Daya", "Barat", "Barat Laut"]
        return dirs[int((deg + 22.5) // 45) % 8]
    
    wind_dir_text = wind_direction_text(wind_dir)

    # Pressure
    if pressure >= 1020:
        pressure_text = "📈 Tekanan tinggi (cuaca stabil kayak hati yang move on)"
    elif pressure >= 1005:
        pressure_text = "⚖️ Normal (aman terkendali)"
    else:
        pressure_text = "📉 Rendah (cuaca bisa drama)"

    # Chance of Rain
    if rain_chance >= 80:
        rain_chance_text = "🌧️ Fix basah (payung? udah gak cukup, butuh kapal 😭)"
    elif rain_chance >= 60:
        rain_chance_text = "🌦️ Besar kemungkinan hujan (jangan sok nekat)"
    elif rain_chance >= 40:
        rain_chance_text = "🌤️ Bisa hujan bisa tidak (cuaca mode indecisive)"
    elif rain_chance >= 20:
        rain_chance_text = "☁️ Kecil kemungkinan (aman sih tapi jangan sombong)"
    else:
        rain_chance_text = "☀️ Santai, langit lagi baik hati"

    # Precipitation
    if precipitation >= 50:
        rain_text = "⛈️ Extreme Rain (ini hujan atau air terjun bocor? 💀)"
    elif precipitation >= 20:
        rain_text = "🌧️ Heavy Rain (siap-siap jadi karakter anime sedih 🌊)"
    elif precipitation >= 5:
        rain_text = "🌦️ Moderate Rain (payung wajib, jangan sok kuat ☔)"
    elif precipitation > 0:
        rain_text = "🌦️ Light Rain (gerimis santai, romantis dikit 😌)"
    else:
        rain_text = "☀️ No Rain (kering total, AC alam aktif 🔥)"

    # Temperature
    if temp >= 40:
        temp_text = "🔥 Inferno Mode (ini panas apa neraka cabang? 💀)"
    elif temp >= 35:
        temp_text = "🥵 Extremely Hot (kulit auto jadi panggangan sate)"
    elif temp >= 30:
        temp_text = "🌞 Hot (keringetan jalan dikit langsung drama)"
    elif temp >= 26:
        temp_text = "😌 Warm (enak sih, manusiawi banget)"
    elif temp >= 20:
        temp_text = "🌤️ Cool (adem, cocok buat rebahan produktif)"
    elif temp >= 15:
        temp_text = "🧥 Cold (udah mulai butuh jaket dikit)"
    elif temp >= 10:
        temp_text = "🥶 Very Cold (napas bisa keliatan ini)"
    else:
        temp_text = "🧊 Freezing (NPC mode aktif, badan auto kaku)"

    # Feels Like
    if feels_like >= 40:
        feels_text = "🔥 Neraka AC rusak (ini bukan panas lagi)"
    elif feels_like >= 35:
        feels_text = "🥵 Gerah level final boss"
    elif feels_like >= 30:
        feels_text = "🌞 Panas santai tapi mulai lengket"
    elif feels_like >= 25:
        feels_text = "😌 Nyaman kayak kipas angin malam"
    elif feels_like >= 20:
        feels_text = "🌤️ Adem banget, cocok rebahan"
    else:
        feels_text = "🧊 Dingin, tangan auto cari selimut"

    # Humidity
    if humidity >= 90:
        humidity_text = "💦 Lembab brutal (baju kering aja bisa terasa basah 😭)"
    elif humidity >= 80:
        humidity_text = "🥵 Sangat lembab (gerahnya nempel di badan)"
    elif humidity >= 70:
        humidity_text = "😓 Lembab (keringat mulai gampang keluar)"
    elif humidity >= 60:
        humidity_text = "🙂 Cukup lembab (masih nyaman buat aktivitas)"
    elif humidity >= 40:
        humidity_text = "😌 Nyaman (balance banget)"
    elif humidity >= 25:
        humidity_text = "🍃 Agak kering (kulit mulai minta lotion)"
    else:
        humidity_text = "🏜️ Sangat kering (bibir auto pecah-pecah)"
    
    forecast_text = ""

    clock = {
        0:"🕛",1:"🕐",2:"🕑",3:"🕒",4:"🕓",
        5:"🕔",6:"🕕",7:"🕖",8:"🕗",9:"🕘",
        10:"🕙",11:"🕚",12:"🕛",13:"🕐",
        14:"🕑",15:"🕒",16:"🕓",17:"🕔",
        18:"🕕",19:"🕖",20:"🕗",21:"🕘",
        22:"🕙",23:"🕚"
    }
    
    for item in forecast:
    
        hour = int(item["time"][:2])
    
        icon = clock[hour]
    
        desc2 = weather_map.get(item["code"], "🌍 Unknown")
    
        forecast_text += (
            f"{icon} {item['time']}<br>"
            f"{desc2}<br>"
            f"🌡️ {item['temp']}°C • "
            f"🌧️ {item['rain']}% • "
            f"💨 {item['wind']} km/h"
            f"<br><br>"
        )

    # Forecast 3 Days
    forecast_3days = ""
    
    segments = [
        ("🌅 Dini Hari", 0, 4),
        ("🌄 Subuh", 4, 8),
        ("🌤 Pagi", 8, 12),
        ("☀ Siang", 12, 16),
        ("🌇 Sore", 16, 20),
        ("🌙 Malam", 20, 24),
    ]
    
    days = {
        "Monday": "Senin",
        "Tuesday": "Selasa",
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jumat",
        "Saturday": "Sabtu",
        "Sunday": "Minggu"
    }
    
    times = hourly["time"]
    temps = hourly["temperature_2m"]
    codes = hourly["weather_code"]
    probs = hourly["precipitation_probability"]
    winds = hourly["wind_speed_10m"]
    
    for day_index in range(3):
        target_date = daily["sunrise"][day_index][:10]
    
        dt_day = datetime.strptime(target_date, "%Y-%m-%d")
        day_name = days.get(dt_day.strftime("%A"), dt_day.strftime("%A"))
    
        forecast_3days += f"📅 <b>{day_name}</b><br><br>"
    
        for label, start_hour, end_hour in segments:
            indexes = []
    
            for i, t in enumerate(times):
                if t.startswith(target_date):
                    hour = int(t[11:13])
                    if start_hour <= hour < end_hour:
                        indexes.append(i)
    
            if indexes:
                avg_temp = round(sum(temps[i] for i in indexes) / len(indexes))
                avg_wind = round(sum(winds[i] for i in indexes) / len(indexes))
                max_rain = max(probs[i] for i in indexes)
    
                # Cari cuaca yang paling sering muncul
                code_count = {}
                for i in indexes:
                    c = codes[i]
                    code_count[c] = code_count.get(c, 0) + 1
    
                dominant_code = max(code_count, key=code_count.get)
                desc_seg = weather_map.get(dominant_code, "🌍 Unknown")
    
                forecast_3days += (
                    f"<b>{label} ({start_hour:02d}:00-{end_hour-1:02d}:59)</b><br>"
                    f"{desc_seg}<br>"
                    f"🌡️ {avg_temp}°C • "
                    f"🌧️ {max_rain}% • "
                    f"💨 {avg_wind} km/h"
                    f"<br><br>"
                )
    
        forecast_3days += "<br>"

def get_big_cities_weather():
    cities = {
        "🏙️ Jakarta": (-6.2088, 106.8456),
        "⛰️ Bandung": (-6.9175, 107.6191),
        "🏛️ Semarang": (-6.9667, 110.4167),
        "🎓 Yogyakarta": (-7.7956, 110.3695),
        "🌊 Surabaya": (-7.2575, 112.7521),
        "🌧️ Medan": (3.5952, 98.6722),
        "🚢 Palembang": (-2.9761, 104.7754),
        "🛢️ Balikpapan": (-1.2654, 116.8312),
        "🐟 Makassar": (-5.1477, 119.4327),
        "🌴 Denpasar": (-8.6500, 115.2167),
    }

    weather_map = {
        0: "☀️ Clear",
        1: "🌤️ Mainly Clear",
        2: "⛅ Cloudy",
        3: "☁️ Overcast",
        61: "🌧️ Rain",
        63: "🌧️ Moderate Rain",
        65: "⛈️ Heavy Rain",
        80: "🌦️ Showers",
        95: "⛈️ Thunderstorm"
    }

    result = ""

    for city, (lat, lon) in cities.items():
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,weather_code,precipitation_probability,wind_speed_10m"
        )

        data = requests.get(url, timeout=15).json()["current"]

        temp = round(data["temperature_2m"])
        code = data["weather_code"]
        rain = data.get("precipitation_probability", 0)
        wind = round(data.get("wind_speed_10m", 0))

        desc = weather_map.get(code, "🌍 Unknown")

        result += (
            f"<b>{city}</b><br>"
            f"{desc}<br>"
            f"🌡️ {temp}°C • 🌧️ {rain}% • 💨 {wind} km/h"
            f"<br><br>"
        )

    return result

    return (
        temp,
        temp_text,
        humidity,
        humidity_text,
        desc,
        wind,
        wind_text,
        uv_text,
        day_state,
        soil,
        vis_text,
        cloud_cover,
        precipitation,
        rain_text,
        sunrise,
        sunset,
        rain_hours,
        visibility,
        min_visibility,
        max_visibility,
        rain_chance,
        rain_chance_text,
        pressure,
        pressure_text,
        wind_dir,
        wind_dir_text,
        wind_gust,
        gust_text,
        feels_like,
        feels_text,
        forecast,
        forecast_text,
        forecast_3days
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

    TZ = ZoneInfo("Asia/Jakarta")
    now = datetime.now(TZ)

    current_time = now.strftime("%d-%m-%Y %H:%M:%S")

    previous_time = status.get("weather_latest_update")

    raw_compare = "00:00:00"
    pretty_compare = "First Run"

    if previous_time:
        try:
            old = datetime.strptime(
                previous_time,
                "%d-%m-%Y %H:%M:%S"
            ).replace(tzinfo=TZ)

            diff = int((now - old).total_seconds())

            h = diff // 3600
            m = (diff % 3600) // 60
            s = diff % 60

            raw_compare = f"{h:02d}:{m:02d}:{s:02d}"

            if diff < 5:
                pretty_compare = "Baru aja"
            elif diff < 60:
                pretty_compare = "Beberapa detik lalu"
            else:
                parts = []

                if h:
                    parts.append(f"{h} Jam")

                if m:
                    parts.append(f"{m} Menit")

                if s:
                    parts.append(f"{s} Detik")

                pretty_compare = " ".join(parts) + " lalu"

        except Exception:
            raw_compare = "Unknown"
            pretty_compare = "Unknown"

    status["weather_last_update"] = previous_time or current_time
    status["weather_latest_update"] = current_time
    status["weather_compare"] = raw_compare
    status["weather_compare_pretty"] = pretty_compare

    save_status(status)

    return (
        current_time,
        status["weather_last_update"],
        raw_compare,
        pretty_compare
    )

def main():
    (
        temp,
        temp_text,
        humidity,
        humidity_text,
        desc,
        wind,
        wind_text,
        uv_text,
        day_state,
        soil,
        vis_text,
        cloud_cover,
        precipitation,
        rain_text,
        sunrise,
        sunset,
        rain_hours,
        visibility,
        min_visibility,
        max_visibility,
        rain_chance,
        rain_chance_text,
        pressure,
        pressure_text,
        wind_dir,
        wind_dir_text,
        wind_gust,
        gust_text,
        feels_like,
        feels_text,
        forecast,
        forecast_text,
        forecast_3days
    ) = get_weather()
    (
        latest_update,
        last_update,
        compare_raw,
        compare_pretty
    ) = update_weather_tracker()
    aq = get_air_quality()
    aqi = aq["aqi"]
    aqi_text = aq["aqi_text"]
    pm25 = aq["pm25"]
    pm10 = aq["pm10"]
    big_cities = get_big_cities_weather()

    days = {
        "Monday": "Senin",
        "Tuesday": "Selasa",
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jumat",
        "Saturday": "Sabtu",
        "Sunday": "Minggu"
    }

    months = {
            "January": "Januari",
            "February": "Februari",
            "March": "Maret",
            "April": "April",
            "May": "Mei",
            "June": "Juni",
            "July": "Juli",
            "August": "Agustus",
            "September": "September",
            "October": "Oktober",
            "November": "November",
            "December": "Desember"
        }
    
    dt = datetime.strptime(last_update, "%d-%m-%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Asia/Jakarta"))
    
    hari = days[dt.strftime("%A")]
    bulan = months[dt.strftime("%B")]
    
    last_update_id = (
        f"{hari}, "
        f"{dt.day} "
        f"{bulan} "
        f"{dt.year} "
        f"{dt.strftime('%H:%M:%S')}"
    )

    dt_latest = datetime.strptime(latest_update, "%d-%m-%Y %H:%M:%S").replace(tzinfo=ZoneInfo("Asia/Jakarta"))
    
    hari_latest = days[dt_latest.strftime("%A")]
    bulan_latest = months[dt_latest.strftime("%B")]
    
    latest_update_id = (
        f"{hari_latest}, "
        f"{dt_latest.day} "
        f"{bulan_latest} "
        f"{dt_latest.year} "
        f"{dt_latest.strftime('%H:%M:%S')}"
    )

    block = f"""{START_MARKER}
<div align="center">

### 🌦️ Weather in Me
##### (Updated Approximately Every 1 to 4 Hour)*
##### 🟢 Latest: {latest_update_id}  
##### 🟡 Previous: {last_update_id}  
##### ⏱️ Update Gap: {compare_pretty}<br><br>

*its up to Github Cron Job to take, and its wild ngl 💀

━━━━━━━━━━━━━━━━━━
### 📍 Current

**{desc}**

🌡️ Temperature: {temp}°C  ({temp_text})<br>
🌡 Feels Like: {feels_like}°C ({feels_text})<br>
🌧 Chance of Rain: {rain_chance}% ({rain_chance_text})<br>
💨 Wind Speed: {wind} km/h  ({wind_text})<br>

━━━━━━━━━━━━━━━━━━

### ⏳ Forecast (Next 5 Hours)

{forecast_text}

━━━━━━━━━━━━━━━━━━

### 📆 Forecast 3 days ahead

<details>
<summary>🌤️ Lihat detail cuaca 3 hari ke depan</summary>

{forecast_3days}

</details>

━━━━━━━━━━━━━━━━━━

### Forecast Big Cities Indonesia

<details>
<summary>🏙️ Lihat cuaca kota besar Indonesia</summary>

<br>

{big_cities}

</details>

━━━━━━━━━━━━━━━━━━

### 🌍 Environment

☁️ Cloud Cover: {cloud_cover}%  
🌡 Pressure: {pressure} hPa ({pressure_text})<br>
☔ Precipitation: {precipitation} mm  ({rain_text})<br>
🌧️ Rain Hours: {rain_hours} h

💧 Humidity: {humidity}% ({humidity_text})<br>
🌱 Soil Temp: {soil}°C

😷 Air Quality Index: {aqi} ({aqi_text})<br>
🌫️ PM2.5: {pm25}<br>
🌫️ PM10: {pm10}<br>

💨 Wind Gust: {wind_gust} km/h ({gust_text})<br>
🧭 Wind Direction: {wind_dir}° ({wind_dir_text})<br>
☀️ UV: {uv_text}  
🌗 Time: {day_state}

🌅 Sunrise: {sunrise}  
🌇 Sunset: {sunset}

👀 Visibility: {visibility} m  ({vis_text})<br>
🔻 Min: {min_visibility} m  
🔺 Max: {max_visibility} m

</div>
{END_MARKER}"""

    update_readme(block)

    print("Weather updated!")

if __name__ == "__main__":
    main()
