from typing import Annotated

from fastapi import APIRouter, Path
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from ..config.api_keys import API_KEY
from ..config.urls import BASE_URL
from ..response_models.weather import map_weather_to_response
from ..routers.auth import get_current_user, get_db
from ..services.weather_services import (
    fetch_weather_data, fetch_weather_data_for_favourites_cities)

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/{city}", status_code=status.HTTP_200_OK)
async def get_weather(
    user: user_dependency,
    db: db_dependency,
    city: str = Path(description="Name of city"),
):
    weather_data = fetch_weather_data(BASE_URL, API_KEY, city, user, db)
    return map_weather_to_response(weather_data, city)


@router.get("/favourite/", status_code=status.HTTP_200_OK)
async def get_weather_for_favourites_city(user: user_dependency, db: db_dependency):
    result = fetch_weather_data_for_favourites_cities(BASE_URL, API_KEY, user, db)
    return result
