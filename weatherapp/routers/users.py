from typing import Annotated

from fastapi import APIRouter, Path
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from ..models import User
from ..response_models.users import map_users_to_response
from ..routers.auth import get_current_user, get_db
from ..schemas.users import CreateUserRequest, EditUserRequest
from ..services.user_service import create_user, delete_user, edit_user
from ..services.validation_service import (validate_role, validate_user_found,
                                           validate_username_exist,
                                           verify_admin_user)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_user(
    create_user_request: CreateUserRequest, user: user_dependency, db: db_dependency
):
    verify_admin_user(user)
    validate_username_exist(create_user_request.username, user, db)
    validate_role(create_user_request.role, user)
    create_user(create_user_request, db)
    return {"message": "User created successfully."}


@router.get("/show", status_code=status.HTTP_200_OK)
async def show_users(user: user_dependency, db: db_dependency):
    verify_admin_user(user)
    users_model = db.query(User).all()
    return map_users_to_response(users_model)


@router.put("/update/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_users(
    edit_user_request: EditUserRequest,
    user: user_dependency,
    db: db_dependency,
    user_id: int = Path(gt=0),
):
    verify_admin_user(user)
    user_model = validate_user_found(user_id, user, db)
    edit_user(edit_user_request, user_model, user, db)


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users(
    user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)
):
    verify_admin_user(user)
    user_model = validate_user_found(user_id, user, db)
    delete_user(user_model, db)
