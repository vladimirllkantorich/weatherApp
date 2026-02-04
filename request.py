import requests
from datetime import datetime, timezone, timedelta




def WeatherNowJson(city, API_KEY):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}

    r = requests.get(url, params=params, timeout=20)
    #print(r.status_code)
    data = r.json()
    return(data)



def WeatherFiveJson(city, API_KEY):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "en"}

    r = requests.get(url, params=params, timeout=20)
    data = r.json()
    return data



def to_city_dt(ts_utc: int, tz_shift: int) -> datetime:
    tz = timezone(timedelta(seconds=int(tz_shift)))
    return datetime.fromtimestamp(int(ts_utc), tz=timezone.utc).astimezone(tz)



