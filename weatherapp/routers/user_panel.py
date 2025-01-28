from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from ..models import User
from ..response_models.user_panel import user_detail_to_response
from ..schemas.users import EditPasswordRequest
from ..services.user_service import edit_password
from ..services.validation_service import validate_password_reset, verify_user
from .auth import get_current_user, get_db

router = APIRouter(
    prefix="/user_panel",
    tags=["user_panel"],
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/detail", status_code=status.HTTP_200_OK)
async def show_user_detail(user: user_dependency, db: db_dependency):
    verify_user(user)
    user_model = db.query(User).filter(User.id == user["id"]).first()
    return user_detail_to_response(user_model)


@router.put("/reset_password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    edit_password_request: EditPasswordRequest, user: user_dependency, db: db_dependency
):
    verify_user(user)
    user_model = validate_password_reset(edit_password_request, user["id"], user, db)
    edit_password(edit_password_request, user_model, db)
