from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from starlette import status

from ..response_models.city import map_favourites_cities_to_response
from ..routers.auth import get_current_user, get_db
from ..schemas.city import AddCityRequest
from ..services.city_service import add_city, delete_city, edit_city
from ..services.validation_service import (validate_favourite_city_exist,
                                           validate_favourite_city_name_exist,
                                           validate_found_user_favourite_city,
                                           verify_user)

router = APIRouter(prefix="/favourites", tags=["favourites"])

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_favourite_city(
    add_city_request: AddCityRequest, db: db_dependency, user: user_dependency
):
    verify_user(user)
    validate_favourite_city_name_exist(add_city_request.city, user, db)
    add_city(add_city_request, user, db)
    return {"message": "City added successfully."}


@router.get("/show", status_code=status.HTTP_200_OK)
async def show_favourites_cities(db: db_dependency, user: user_dependency):
    verify_user(user)
    city_models = validate_found_user_favourite_city(user, db)
    return map_favourites_cities_to_response(city_models)


@router.put("/update/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_favourite_city(
    edit_city_request: AddCityRequest,
    user: user_dependency,
    db: db_dependency,
    city_id: int = Path(gt=0),
):
    verify_user(user)
    validate_favourite_city_name_exist(edit_city_request.city, user, db)
    city_model = validate_favourite_city_exist(city_id, user, db)
    edit_city(city_model, edit_city_request, db)


@router.delete("/delete/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favourite_city(
    user: user_dependency, db: db_dependency, city_id: int = Path(gt=0)
):
    verify_user(user)
    city_model = validate_favourite_city_exist(city_id, user, db)
    delete_city(city_model, db)
