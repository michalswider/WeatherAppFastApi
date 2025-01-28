def map_favourite_cities_to_response(cities):
    results = []
    for city in cities:
        results.append(
            {
                "id": city.id,
                "city": city.city_name,
            }
        )
    return results
