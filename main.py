import streamlit as st
from datetime import datetime

from request import WeatherNowJson, WeatherFiveJson
from weathernow import ShowWeatherNow
from charts import ShowWeatherFive
from user import UserStore, AppUser, AuthError
from admin_panel import render_admin_stats

st.set_page_config(layout="wide")
st.title("Weather app")

if "store" not in st.session_state:
    st.session_state.store = UserStore()
if "user" not in st.session_state:
    st.session_state.user = None
if "cur_data" not in st.session_state:
    st.session_state.cur_data = None
if "city_used" not in st.session_state:
    st.session_state.city_used = ""
if "city_input" not in st.session_state:
    st.session_state.city_input = ""

store: UserStore = st.session_state.store

api_key = st.secrets.get("api_key")
if not api_key:
    st.error('Missing "api_key" in secrets.toml')
    st.stop()

admin_pwd = st.secrets.get("admin_password")
if not admin_pwd:
    st.error('Missing "admin_password" in secrets.toml')
    st.stop()

admin_nick = str(st.secrets.get("admin_nickname", "admin")).strip() or "admin"
admin_home = str(st.secrets.get("admin_home_city", "Jerusalem")).strip() or "Jerusalem"
store.ensure_admin(admin_nick, admin_home, admin_pwd)

def canon_city(data: dict, fallback: str) -> str:
    name = str(data.get("name", "")).strip()
    return name or fallback

def load_current(city: str) -> dict:
    return WeatherNowJson(city, api_key)

def load_forecast(city: str) -> dict:
    return WeatherFiveJson(city, api_key)

def show_current(city: str) -> str | None:
    data = load_current(city)
    if str(data.get("cod", "")) != "200":
        st.error(data.get("message", "City error"))
        st.session_state.cur_data = None
        st.session_state.city_used = ""
        return None

    c = canon_city(data, city)
    st.session_state.cur_data = data
    st.session_state.city_used = c
    ShowWeatherNow(data)
    return c

st.sidebar.header("Account")

user: AppUser | None = st.session_state.user

if user is None:
    mode = st.sidebar.radio("Menu", ["Login", "Register"], key="auth_mode_widget")

    if mode == "Register":
        nick = st.sidebar.text_input("Nickname", key="reg_nick")
        home_city = st.sidebar.text_input("Home city", key="reg_home")
        pwd = st.sidebar.text_input("Password", type="password", key="reg_pwd")
        pwd2 = st.sidebar.text_input("Repeat password", type="password", key="reg_pwd2")

        if st.sidebar.button("Create account"):
            if pwd != pwd2:
                st.sidebar.error("Passwords do not match")
                st.stop()

            with st.spinner("Loading weather for home city..."):
                data = load_current(home_city)

            if str(data.get("cod", "")) != "200":
                st.sidebar.error(data.get("message", "City error"))
                st.stop()

            canon_home = canon_city(data, home_city)

            try:
                st.session_state.user = store.add_user(nickname=nick, home_city=canon_home, password=pwd)
            except AuthError as e:
                st.sidebar.error(str(e))
                st.stop()

            st.session_state.cur_data = data
            st.session_state.city_used = canon_home
            st.session_state.city_input = canon_home
            st.session_state.user.add_city(canon_home)

            for k in ("reg_nick", "reg_home", "reg_pwd", "reg_pwd2"):
                st.session_state.pop(k, None)
            st.rerun()

    else:
        nick = st.sidebar.text_input("Nickname", key="login_nick")
        pwd = st.sidebar.text_input("Password", type="password", key="login_pwd")

        if st.sidebar.button("Login"):
            try:
                st.session_state.user = store.authenticate(nickname=nick, password=pwd)
            except AuthError as e:
                st.sidebar.error(str(e))
                st.stop()

            st.session_state.city_input = st.session_state.user.home_city
            st.session_state.cur_data = None
            st.session_state.city_used = ""

            for k in ("login_nick", "login_pwd"):
                st.session_state.pop(k, None)
            st.rerun()

else:
    st.sidebar.success(f"Logged in as: {user.nickname}")
    if st.sidebar.button("Switch account"):
        st.session_state.user = None
        st.session_state.cur_data = None
        st.session_state.city_used = ""
        st.session_state.city_input = ""
        st.rerun()

user = st.session_state.user

if user is not None:
    with st.sidebar.expander("My stats", expanded=False):
        st.write("Home city:", user.home_city)
        st.write("Total requests:", user.total_requests())
        st.write("Unique cities:", user.unique_cities())
        top = user.top_cities(5)
        st.write("Top cities:", ", ".join(f"{c}: {n}" for c, n in top) if top else "—")
        counts = user.city_counts()
        st.dataframe([{"city": c, "requests": n} for c, n in counts.items()], use_container_width=True)

if user is not None and user.role == "admin":
    if st.sidebar.checkbox("Show admin panel", value=False):
        st.divider()
        render_admin_stats(st.session_state.store, user)
        st.stop()

now = datetime.now().strftime("%H:%M")
h1, h2 = st.columns([6, 1], vertical_alignment="bottom")
with h1:
    st.markdown("**City name**")
with h2:
    st.markdown(f"**your time {now}**")

if user is None:
    st.info("Login or register in the sidebar to continue.")
    st.stop()

city = st.text_input(
    "city",
    value=st.session_state.city_input,
    placeholder="search",
    label_visibility="hidden",
).strip()
st.session_state.city_input = city

b1, b2 = st.columns([1, 1])
get_btn = b1.button("Get weather now")
draw_btn = b2.button("Get forecast", disabled=(not city))

if (not get_btn) and st.session_state.cur_data is None and city:
    with st.spinner("Loading current weather..."):
        show_current(city)

if get_btn:
    if not city:
        st.warning("Please enter a city name.")
    else:
        with st.spinner("Loading current weather..."):
            c = show_current(city)
        if c:
            st.session_state.user.add_city(c)

if draw_btn:
    used_city = city
    cur = st.session_state.cur_data
    if isinstance(cur, dict) and str(cur.get("cod", "")) == "200":
        ShowWeatherNow(cur)
        used_city = st.session_state.city_used or city

    st.divider()

    with st.spinner("Loading forecast..."):
        fc = load_forecast(used_city)

    if str(fc.get("cod", "")) != "200":
        st.error(fc.get("message", "Forecast error"))
    else:
        ShowWeatherFive(fc, points=40)
        st.session_state.user.add_city(used_city)
