import requests
from location_parser import get_location_key_by_city
from secretka import accuweather_api_key


def check_bad_weather(temp: object, wind_speed_kmh: object, precipitation_prob: object) -> object:
    if temp < 0 or temp > 35 or wind_speed_kmh > 50 or precipitation_prob > 70:
        return 'Плохие'
    return 'Хорошие'


def get_weather_status(city):
    try:
        # Получаем ключ для города
        location_key = get_location_key_by_city(city)

        if not location_key:
            return {"error": f"Не удалось найти город: {city}"}

        current_url = (
            f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
            f"?apikey={accuweather_api_key}&language=ru-RU&details=true&metric=true"
        )

        forecast_url = (
            f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
            f"?apikey={accuweather_api_key}&language=ru-RU&details=true&metric=true"
        )

        # Данные о текущей погоде
        response_current = requests.get(current_url)
        response_current.raise_for_status()  # Проверка на ошибки при запросе
        data_current = response_current.json()

        if data_current:
            weather_current = data_current[0]
            temperature = weather_current.get('Temperature', {}).get('Metric', {}).get('Value', 'хз')
            humidity = weather_current.get('RelativeHumidity', 'хз')
            wind_speed_kmh = weather_current.get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value', 'хз')
        else:
            temperature = humidity = wind_speed_kmh = 'хз'

        # Данные об осадках
        response_forecast = requests.get(forecast_url)
        response_forecast.raise_for_status()  # Проверка на ошибки при запросе
        data_forecast = response_forecast.json()

        if data_forecast and 'DailyForecasts' in data_forecast:
            forecast_day = data_forecast['DailyForecasts'][0]
            precipitation_probability = forecast_day.get('Day', {}).get('PrecipitationProbability', 'хз')
        else:
            precipitation_probability = 'хз'

        # Оценка погодных условий
        weather_status = check_bad_weather(temperature, wind_speed_kmh, precipitation_probability)

        return {
            "city": city,
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed_kmh": wind_speed_kmh,
            "precipitation_probability": precipitation_probability,
            "weather_status": weather_status
        }

    except requests.RequestException as e:
        return {"error": f"Ошибка подключения к серверу: {e}"}

def get_weather_forecast(city, interval=1):
    try:
        location_key = get_location_key_by_city(city)

        if not location_key:
            return {"error": f"Не удалось найти город: {city}"}

        forecast_url = (
            f"http://dataservice.accuweather.com/forecasts/v1/daily/{interval}day/{location_key}"
            f"?apikey={accuweather_api_key}&language=ru-RU&details=true&metric=true"
        )
        response_forecast = requests.get(forecast_url)
        response_forecast.raise_for_status()
        data_forecast = response_forecast.json()

        if data_forecast and 'DailyForecasts' in data_forecast:
            forecast = [
                {
                    "date": day.get("Date"),
                    "temperature": day.get("Temperature", {}).get("Maximum", {}).get("Value", 0),
                    "wind_speed_kmh": day.get("Day", {}).get("Wind", {}).get("Speed", {}).get("Value", 0),
                    "precipitation_probability": day.get("Day", {}).get("PrecipitationProbability", 0),
                    "weather_status": check_bad_weather(
                        day.get("Temperature", {}).get("Maximum", {}).get("Value", 0),
                        day.get("Day", {}).get("Wind", {}).get("Speed", {}).get("Value", 0),
                        day.get("Day", {}).get("PrecipitationProbability", 0)
                    )
                }
                for day in data_forecast['DailyForecasts']
            ]
            return {"forecast": forecast}

        return {"error": "Нет данных прогноза"}

    except requests.RequestException as e:
        return {"error": f"Ошибка подключения к серверу: {e}"}
