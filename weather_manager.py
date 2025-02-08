import requests

def get_weather(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city
    response = requests.get(complete_url)
    if response.status_code == 200:
        data = response.json()
        if "main" in data:
            temp = data["main"]["temp"] - 273.15  # Convert Kelvin to Celsius
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            return temp, humidity, description
    return None  # Return None if the weather data is not found 