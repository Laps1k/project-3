import requests
from secretka import accuweather_api_key

def get_location_key_by_geoposition(latitude, longitude):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={accuweather_api_key}&q={latitude},{longitude}&language=ru-RU"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data["Key"]
        else:
            print("Не найдено.")
            return None
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")
        return None

def get_location_key_by_city(city_name):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={accuweather_api_key}&q={city_name}&language=ru-RU"
    response = requests.get(url)
    if response.status_code == 200:
        city_data = response.json()
        if city_data:
            return city_data[0]["Key"]
        else:
            print("Не найдено.")
            return None
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")
        return None

