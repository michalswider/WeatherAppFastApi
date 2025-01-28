from datetime import datetime
from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from ..exceptions import (ExistException, InvalidException, NotFoundException,
                          PermissionException)
from ..models import User, UserFavouriteCities, WeatherCache
from ..routers.auth import bcrypt_context, get_db
from ..schemas.users import EditPasswordRequest

db_dependency = Annotated[Session, Depends(get_db)]


def verify_user(user: dict):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )


def verify_admin_user(user: dict):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed"
        )
    if user.get("role") != "admin":
        raise PermissionException(detail="Permission Denied", user=user["username"])


def validate_username_exist(username: str, user: dict, db: db_dependency):
    user_model = db.query(User).filter(User.username == username).first()
    if user_model:
        raise ExistException(detail="Username already exists", user=user["username"])


def validate_user_found(user_id: int, user: dict, db: db_dependency):
    user_model = db.query(User).filter(User.id == user_id).first()
    if user_model is None:
        raise NotFoundException(detail="User not found", user=user["username"])
    return user_model


def validate_role(role: str, user: dict):
    if role not in ("user", "admin"):
        raise InvalidException(
            detail=f"Invalid status: {role}. Allowed status are 'user', 'admin'.",
            user=user["username"],
        )


def validate_favourite_city_name_exist(city: str, user: dict, db: db_dependency):
    city_model = (
        db.query(UserFavouriteCities)
        .filter(
            UserFavouriteCities.user_id == user["id"],
            UserFavouriteCities.city_name == city.capitalize(),
        )
        .first()
    )
    if city_model:
        raise ExistException(
            detail=f"Favourite city: {city} already exist.", user=user["username"]
        )


def validate_found_user_favourite_city(user: dict, db: db_dependency):
    city_models = (
        db.query(UserFavouriteCities)
        .filter(UserFavouriteCities.user_id == user["id"])
        .all()
    )
    if not city_models:
        raise NotFoundException(detail="Cities not found", user=user["username"])
    return city_models


def validate_favourite_city_exist(city_id: int, user: dict, db: db_dependency):
    city_model = (
        db.query(UserFavouriteCities)
        .filter(
            UserFavouriteCities.user_id == user["id"], UserFavouriteCities.id == city_id
        )
        .first()
    )
    if city_model is None:
        raise ExistException(detail="City not exist", user=user["username"])
    return city_model


def check_weather_cache(city: str, db: db_dependency):
    weather_model = (
        db.query(WeatherCache)
        .filter(
            WeatherCache.city == city.capitalize(),
            WeatherCache.query_date == datetime.now().date(),
        )
        .first()
    )
    if weather_model:
        return weather_model.weather_data
    return None


def validate_password_reset(
    request: EditPasswordRequest, user_id: int, user: dict, db: db_dependency
):
    user_model = db.query(User).filter(User.id == user_id).first()
    if not bcrypt_context.verify(request.old_password, user_model.password_hash):
        raise InvalidException(detail="Error on password change", user=user["username"])
    return user_model
