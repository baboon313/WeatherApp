from flask import Flask, render_template, request, redirect, url_for
import requests


app = Flask(__name__)

API_KEY = ""


def get_weather(city):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city}&language=ru-ru"
    data = requests.get( url).json()
    if data:
        location_key = data[0]['Key']
        weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={API_KEY}&language=ru-ru&details=true"
        weather_data = requests.get(weather_url).json()
        if weather_data:
            return {
                "city": city,
                "temperature": weather_data[0]['Temperature']['Metric']['Value'],
                "humidity": weather_data[0]['RelativeHumidity'],
                "wind_speed": round(weather_data[0]['Wind']['Speed']['Metric']['Value']/3.6, 2),
                "precipitation": weather_data[0]['HasPrecipitation'],
                "weather_text": weather_data[0]['WeatherText']
            }
    return None


def check_bad_weather(weather, temp, humidity, wind):
    conditions = {}

    if temp and float(temp) + 4 >= weather['temperature'] >= float(temp) - 4:
        conditions['temperature'] = 'Температура хорошая'
    elif 34 >= weather['temperature'] >= 0:
        conditions['temperature'] = 'Температура хорошая'
    else:
        if temp:
            conditions['temperature'] = 'Температура плохая'
        else:
            conditions['temperature'] = 'Температура плохая'

    if humidity and float(humidity) + 10 >= weather['humidity'] >= float(humidity) - 10:
        conditions['humidity'] = 'Влажность хорошая'
    elif 80 >= weather['humidity'] >= 60:
        conditions['humidity'] = 'Влажность хорошая'
    else:
        if humidity:
            conditions['humidity'] = 'Влажность плохая'
        else:
            conditions['humidity'] = 'Влажность плохая'

    if wind and float(wind) >= weather['wind_speed']:
        conditions['wind_speed'] = 'Скорость ветра хорошая'
    elif 15 >= weather['wind_speed']:
        conditions['wind_speed'] = 'Скорость ветра хорошая'
    else:
        if wind:
            conditions['wind_speed'] = 'Скорость ветра плохая'
        else:
            conditions['wind_speed'] = 'Скорость ветра плохая'

    return conditions


@app.route('/')
def index():
    return render_template('main.html')


@app.route('/check_weather', methods=['POST'])
def check_weather():
    start_city = request.form['start_city']
    end_city = request.form['end_city']

    preferenced_temp = request.form['temperature']
    preferenced_humidity = request.form['humidity']
    preferenced_wind_speed = request.form['wind_speed']
    start_weather = get_weather(start_city)
    end_weather = get_weather(end_city)
    if not start_weather or not end_weather:
        return render_template('error.html', error_message='Города не найдены')

    try:
        start = check_bad_weather(start_weather, preferenced_temp, preferenced_humidity,
                                            preferenced_wind_speed)
        end = check_bad_weather(end_weather, preferenced_temp, preferenced_humidity,
                                        preferenced_wind_speed)
    except:
        return render_template('error.html', error_message='Произошла ошибка при работе с API. Попробуйте новый ключ')

    return render_template('res.html', start_weather=start_weather, end_weather=end_weather,
                           start_conditions=start, end_conditions=end)


if __name__ == '__main__':
    app.run(debug=True)
