from datetime import datetime
from typing import Annotated

import requests
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from ..exceptions import (ConnectionException, InvalidException,
                          NotFoundException, RequestException,
                          TimeoutException)
from ..handlers import logger
from ..models import WeatherCache
from ..response_models.errors import (connection_error_response_model,
                                      http_error_response_model,
                                      invalid_error_response_model,
                                      not_found_error_response_model,
                                      request_error_response_model,
                                      timeout_error_response_model)
from ..response_models.weather import map_weather_to_response
from ..routers.auth import get_db
from ..services.validation_service import (check_weather_cache,
                                           validate_found_user_favourite_city)

db_dependency = Annotated[Session, Depends(get_db)]


def fetch_weather_data_from_api(
    url: str, api: str, city: str, user: dict, db: db_dependency
):
    params = {"q": city, "appid": api, "units": "metric", "lang": "en"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        add_weather_cache(response.json(), city, db)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 404:
            raise NotFoundException(detail="City not found", user=user["username"])
        elif http_err.response.status_code == 400:
            raise InvalidException(
                detail="Invalid city name or missing parameters in the request.",
                user=user["username"],
            )
        else:
            raise HTTPException(
                status_code=http_err.response.status_code,
                detail=f"HTTP error occurred: {http_err.response.text}",
            )
    except requests.exceptions.ConnectionError:
        raise ConnectionException(detail="Connection error")
    except requests.exceptions.Timeout:
        raise TimeoutException(detail="Request timeout")
    except requests.exceptions.RequestException as req_err:
        raise RequestException(detail=f"Network error: {req_err}")


def fetch_weather_data(
    url: str, api: str, city: str, user: dict, db: db_dependency
) -> dict:
    cache_status = check_weather_cache(city, db)
    if cache_status is not None:
        return cache_status
    else:
        return fetch_weather_data_from_api(url, api, city, user, db)


def fetch_weather_data_for_favourites_cities(
    url: str, api: str, user: dict, db: db_dependency
):
    city_model = validate_found_user_favourite_city(user, db)
    username = user["username"]
    result = []
    for i in city_model:
        cache_status = check_weather_cache(str(i.city_name), db)
        if cache_status is not None:
            result.append(map_weather_to_response(cache_status, str(i.city_name)))
        else:
            try:
                weather_data = fetch_weather_data_from_api(
                    url, api, str(i.city_name), user, db
                )
                result.append(map_weather_to_response(weather_data, str(i.city_name)))
            except NotFoundException as notfound_err:
                logger.warning(
                    f"Not found city: {str(i.city_name)}, Status Code: {notfound_err.status_code}, user: {username}"
                )
                result.append(
                    not_found_error_response_model(
                        str(i.city_name), notfound_err.detail
                    )
                )
            except InvalidException as invalid_err:
                logger.warning(
                    f"Invalid input for city: {str(i.city_name)}, Error: {invalid_err.detail}"
                )
                result.append(
                    invalid_error_response_model(str(i.city_name), invalid_err.detail)
                )
            except HTTPException as http_err:
                logger.warning(
                    f"HTTP error for city: {str(i.city_name)}, Error: {http_err.detail}"
                )
                result.append(
                    http_error_response_model(
                        str(i.city_name), http_err.status_code, http_err.detail
                    )
                )
            except ConnectionException as connection_err:
                logger.warning(
                    f"Connection error for city: {str(i.city_name)}, Error: {connection_err.detail}"
                )
                result.append(
                    connection_error_response_model(
                        str(i.city_name), connection_err.detail
                    )
                )
            except TimeoutException as timeout_err:
                logger.warning(
                    f"Timeout occurred for city: {str(i.city_name)}, Error: {timeout_err.detail}"
                )
                result.append(
                    timeout_error_response_model(str(i.city_name), timeout_err.detail)
                )
            except RequestException as req_err:
                logger.warning(
                    f"Network error for city: {str(i.city_name)}, Error: {req_err.detail}"
                )
                result.append(
                    request_error_response_model(str(i.city_name), req_err.detail)
                )
    return result


def add_weather_cache(weather_date: dict, city: str, db: db_dependency):
    current_date = datetime.now().date()
    weather_model = WeatherCache(
        city=city.capitalize(), weather_data=weather_date, query_date=current_date
    )
    db.add(weather_model)
    db.commit()


def delete_old_weather_cache(db: db_dependency):
    current_time = datetime.now().date()
    db.query(WeatherCache).filter(WeatherCache.query_date < current_time).delete()
    db.commit()
