import requests
from datetime import datetime, timezone, timedelta


def WeatherNowJson(city: str, api_key: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    r = requests.get(url, params=params, timeout=20)
    return r.json()


def WeatherFiveJson(city: str, api_key: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "en"}
    r = requests.get(url, params=params, timeout=20)
    return r.json()


def to_city_dt(ts_utc: int, tz_shift: int) -> datetime:
    tz = timezone(timedelta(seconds=int(tz_shift)))
    return datetime.fromtimestamp(int(ts_utc), tz=timezone.utc).astimezone(tz)
