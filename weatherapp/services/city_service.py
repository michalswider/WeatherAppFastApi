from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.orm import Session

from ..models import UserFavouriteCities
from ..routers.auth import get_current_user, get_db
from ..schemas.city import AddCityRequest

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def add_city(request: AddCityRequest, user: user_dependency, db: db_dependency):
    city_model = UserFavouriteCities(
        city_name=request.city.capitalize(), user_id=user["id"]
    )
    db.add(city_model)
    db.commit()


def edit_city(
    city_model: UserFavouriteCities, request: AddCityRequest, db: db_dependency
):
    city_model.city_name = request.city.capitalize()
    db.add(city_model)
    db.commit()


def delete_city(city_model: UserFavouriteCities, db: db_dependency):
    db.delete(city_model)
    db.commit()
