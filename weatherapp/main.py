from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from .database import Base, engine
from .handlers import setup_exception_handler
from .models import User
from .routers import (administration_tools, auth, favourite_cities, user_panel,
                      users, weather)
from .routers.auth import bcrypt_context, get_db

db_dependency = Annotated[Session, Depends(get_db)]


def create_admin_user(db: db_dependency):
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_model = User(
            first_name="admin",
            last_name="admin",
            username="admin",
            password_hash=bcrypt_context.hash("admin"),
            role="admin",
        )
        db.add(admin_model)
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    try:
        create_admin_user(db)
        yield
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
app = FastAPI(lifespan=lifespan)

setup_exception_handler(app)
app.include_router(users.router)
app.include_router(administration_tools.router)
app.include_router(weather.router)
app.include_router(favourite_cities.router)
app.include_router(user_panel.router)
app.include_router(auth.router)
