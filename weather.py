import os
import requests
from datetime import datetime

# This package is a OFFLINE solution for converting longitude latitude into timezones.
from timezonefinder import TimezoneFinder

# This package is used for converting timezones and handles daylight savings.
from pytz import timezone

tf = TimezoneFinder()

# Grab key from env variables.
api_key = os.environ.get('WEATHER_KEY')

# raises an error if environment variable is not set
assert api_key is not None


def main():
    city = get_city()
    geo_data = get_geo_data(city)

    if geo_data is None:
        print(f'Unable to find {city}.')
        return

    params = {'q': city, 'lat': geo_data[0], 'lon': geo_data[1], 'units': 'imperial', 'APPID': api_key}
    url = 'http://api.openweathermap.org/data/2.5/forecast'
    data = handle_request(url, params)

    time_zone = tf.timezone_at(lng=geo_data[1], lat=geo_data[0])

    if not time_zone:
        print(f'Could not find timezone from {city}')
        return

    tz_target = timezone(time_zone)

    for forecast in data['list']:
        # Why do UTC or local time when you can show it in the city's timezone?
        print(f'At {tz_target.localize(datetime.fromtimestamp(forecast['dt']))} {time_zone} local time the forecast')
        print(f'Temperature is {forecast['main']['temp']}f and it feels like {forecast['main']['feels_like']}f.')
        print(f'Weather shows {forecast['weather'][0]['main']}.')
        print(f'Wind is {forecast['wind']['speed']} MPH, gusts of {forecast['wind']['gust']} MPH')
        print('')


def get_city():
    '''
    Gets city from user's input.
    '''
    city = input('Input your city you want to get weather for: ')

    if not city or len(city) == 0 or not isinstance(city, str):
        print("Input correct city please.")
        return get_city()

    return city.capitalize()


def get_geo_data(city):
    '''
    Converts user inputted city into longitude latitude coordinates
    :param city: User's City.
    :return:
    '''
    params = {'q': city, 'limit': '1', 'APPID': api_key}
    url = 'http://api.openweathermap.org/geo/1.0/direct'
    data = handle_request(url, params)

    if len(data) == 0 or data is None:
        return None

    try:
        geo_data = [data[0]['lat'], data[0]['lon']]
        return geo_data
    except Exception as e:
        print(e)


def handle_request(url, params):
    '''
    Manages error handling for our requests.
    :param url: API URL
    :param params: API parameters
    :return: json if successful or None if not.
    '''
    response = requests.get(url, params)

    if response.status_code == 200:
        return response.json()
    if response.status_code == 404:
        return None


main()