import streamlit as st
from request import to_city_dt
import pandas as pd
import plotly.graph_objects as go





def ShowWeatherFive(data: dict, points: int = 40) -> None:
    city = data.get("city", {}) or {}
    name = city.get("name", "Unknown")
    tz_shift = int(city.get("timezone", 0))

    items = data.get("list") or []
    rows = []

    for it in items[:points]:
        ts = it.get("dt")
        main = it.get("main", {}) or {}
        wind = it.get("wind", {}) or {}

        t = main.get("temp")
        f = main.get("feels_like")
        w = wind.get("speed")

        rows.append({"dt": to_city_dt(ts, tz_shift), "temp": float(t), "feels": float(f), "wind": float(w)})

    df = pd.DataFrame(rows)

    tab1, tab2 = st.tabs(["Temp vs Feels", "Wind"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["dt"], y=df["temp"], mode="lines+markers", name="Temp"))
        fig.add_trace(go.Scatter(x=df["dt"], y=df["feels"], mode="lines+markers", name="Feels like"))
        fig.update_layout(
            title=f"Temperature forecast — {name}",
            hovermode="x unified",
            xaxis=dict(title="Local time", rangeslider=dict(visible=True)),
            yaxis=dict(title="°C"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=10, r=10, t=60, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["dt"], y=df["wind"], mode="lines+markers", name="Wind"))
        fig.update_layout(
            title=f"Wind forecast — {name}",
            hovermode="x unified",
            xaxis=dict(title="Local time", rangeslider=dict(visible=True)),
            yaxis=dict(title="m/s"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=10, r=10, t=60, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
