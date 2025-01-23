def map_weather_to_response(weather_data: dict, city: str) -> dict:
    temperature = round(weather_data["main"]["temp"])
    min_temp = round(weather_data["main"]["temp_min"])
    max_temp = round(weather_data["main"]["temp_max"])
    weather_conditions = weather_data["weather"][0]["description"]
    return {
        "City": city.capitalize(),
        "Temperature": temperature,
        "Minimal temperature": min_temp,
        "Maximal temperature": max_temp,
        "Weather conditions": weather_conditions,
    }
