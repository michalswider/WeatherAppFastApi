from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from ..routers.auth import get_current_user, get_db
from ..services.validation_service import verify_admin_user
from ..services.weather_services import delete_old_weather_cache

router = APIRouter(
    prefix="/administration_tools",
    tags=["administration tools"],
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/cleanup", status_code=status.HTTP_201_CREATED)
async def cleanup_old_weather_cache(user: user_dependency, db: db_dependency):
    verify_admin_user(user)
    delete_old_weather_cache(db)
    return {"message": "Old weather cache cleaned up!"}
