import streamlit as st
from datetime import datetime

from request import  WeatherNowJson, WeatherFiveJson
from weathernow import ShowWeatherNow
from charts import ShowWeatherFive

st.set_page_config(layout="wide")
st.title("Weather app")

now = datetime.now().strftime("%H:%M")
h1, h2 = st.columns([6, 1], vertical_alignment="bottom")
with h1:
    st.markdown("**City name**")
with h2:
    st.markdown(f"**your time {now}**")

city = st.text_input("city", placeholder="search", label_visibility="hidden").strip()

# session_state для уже полученной текущей погоды
if "cur_data" not in st.session_state:
    st.session_state.cur_data = None
if "city_used" not in st.session_state:
    st.session_state.city_used = ""

b1, b2 = st.columns([1, 1])
get_btn = b1.button("Get weather now")
draw_btn = b2.button("Get forecast", disabled=(not city))  # ✅ активна сразу после ввода города

if get_btn:
    if not city:
        st.warning("Please enter a city name.")
    else:
        try:
            with st.spinner("Loading current weather..."):
                data =  WeatherNowJson(city, st.secrets["api_key"])
            cod = str(data.get("cod", ""))

            if cod != "200":
                msg = data.get("message", "Unknown error")
                st.error(f"City error: {msg}")
                st.session_state.cur_data = None
                st.session_state.city_used = ""
            else:
                st.session_state.cur_data = data
                st.session_state.city_used = data.get("name", city)
                ShowWeatherNow(data)

        except KeyError:
            st.error('Missing "api_key" in secrets.toml')
        except Exception as e:
            st.error(f"Error: {e}")

if draw_btn:
    try:
        cur = st.session_state.cur_data
        if isinstance(cur, dict) and str(cur.get("cod", "")) == "200":
            ShowWeatherNow(cur)
            used_city = st.session_state.city_used or city
        else:
            used_city = city

        st.divider()

        with st.spinner("Loading forecast..."):

            fc = WeatherFiveJson(used_city, st.secrets["api_key"])

        cod = str(fc.get("cod", "200"))
        if cod != "200":
            st.error(fc.get("message", "Forecast error"))
        else:
            ShowWeatherFive(fc, points=40)

    except KeyError:
        st.error('Missing "api_key" in secrets.toml')
    except Exception as e:
        st.error(f"Error: {e}")
