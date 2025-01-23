from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.orm import Session

from ..models import User
from ..routers.auth import bcrypt_context, get_db
from ..schemas.users import CreateUserRequest, EditUserRequest
from ..services.validation_service import (validate_role,
                                           validate_username_exist)

db_dependency = Annotated[Session, Depends(get_db)]


def create_user(request: CreateUserRequest, db: db_dependency):
    user_model = User(
        first_name=request.first_name,
        last_name=request.last_name,
        username=request.username,
        password_hash=bcrypt_context.hash(request.password),
        role=request.role,
    )
    db.add(user_model)
    db.commit()


def edit_user(
    request: EditUserRequest, user_model: User, user: dict, db: db_dependency
):
    if request.first_name is not None:
        user_model.first_name = request.first_name
    if request.last_name is not None:
        user_model.last_name = request.last_name
    if request.username is not None:
        validate_username_exist(request.username, user, db)
        user_model.username = request.username
    if request.password is not None:
        user_model.password_hash = bcrypt_context.hash(request.password)
    if request.role is not None:
        validate_role(request.role, user)
        user_model.role = request.role
    db.commit()


def delete_user(user_model: User, db: db_dependency):
    db.delete(user_model)
    db.commit()
