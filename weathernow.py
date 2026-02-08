import streamlit as st
from request import to_city_dt


def ShowWeatherNow(data: dict) -> None:
    name = data.get("name", "Unknown")
    sys = data.get("sys", {}) or {}
    country = sys.get("country", "")
    coord = data.get("coord", {}) or {}
    main = data.get("main", {}) or {}
    wind = data.get("wind", {}) or {}
    weather0 = (data.get("weather") or [{}])[0] or {}

    icon = weather0.get("icon")
    desc = weather0.get("description", "")

    tz_shift = int(data.get("timezone", 0))
    dt_ts = data.get("dt")
    now_city = to_city_dt(dt_ts, tz_shift).strftime("%H:%M") if dt_ts is not None else ""

    st.subheader(f"{name} {f'({country})' if country else ''} — last update {now_city}")

    top_left, top_right = st.columns([3, 1], vertical_alignment="center")

    with top_left:
        lat = coord.get("lat")
        lon = coord.get("lon")
        if lat is not None and lon is not None:
            st.caption(f"Lat: {lat}  |  Lon: {lon}")
        if desc:
            st.write(desc)

    with top_right:
        if icon:
            st.image(f"https://openweathermap.org/img/wn/{icon}@2x.png", width=80)

    st.divider()
    c1, c2, c3, c4 = st.columns(4)

    temp = main.get("temp")
    feels = main.get("feels_like")
    tmin = main.get("temp_min")
    tmax = main.get("temp_max")
    pressure = main.get("pressure")
    humidity = main.get("humidity")

    c1.metric("Temp (°C)", f"{temp:.1f}" if isinstance(temp, (int, float)) else "N/A")
    c2.metric("Feels (°C)", f"{feels:.1f}" if isinstance(feels, (int, float)) else "N/A")
    c3.metric(
        "Min / Max (°C)",
        f"{tmin:.1f} / {tmax:.1f}" if all(isinstance(x, (int, float)) for x in [tmin, tmax]) else "N/A",
    )
    c4.metric("Pressure (hPa)", str(pressure) if pressure is not None else "N/A")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Humidity (%)", str(humidity) if humidity is not None else "N/A")
    c6.metric("Wind (m/s)", str(wind.get("speed")) if wind.get("speed") is not None else "N/A")
    c7.metric(
        "Clouds (%)",
        str((data.get("clouds") or {}).get("all")) if (data.get("clouds") or {}).get("all") is not None else "N/A",
    )

    sunrise_ts = sys.get("sunrise")
    sunset_ts = sys.get("sunset")
    sunrise = to_city_dt(sunrise_ts, tz_shift).strftime("%H:%M") if sunrise_ts is not None else "N/A"
    sunset = to_city_dt(sunset_ts, tz_shift).strftime("%H:%M") if sunset_ts is not None else "N/A"
    c8.metric("Sunrise / Sunset", f"{sunrise} / {sunset}")
