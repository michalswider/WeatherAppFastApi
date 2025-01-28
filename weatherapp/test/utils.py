import pytest
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..models import User, UserFavouriteCities
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "test", "id": 1, "role": "admin"}


@pytest.fixture
def test_user1():
    test_user = User(
        first_name="test",
        last_name="test",
        username="test",
        password_hash=bcrypt_context.hash("test1234"),
        role="user",
    )
    db = TestingSessionLocal()
    db.add(test_user)
    db.commit()
    yield test_user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()


@pytest.fixture
def test_user2():
    test_user = User(
        first_name="test2",
        last_name="test2",
        username="test2",
        password_hash=bcrypt_context.hash("test1234"),
        role="user",
    )
    db = TestingSessionLocal()
    db.add(test_user)
    db.commit()
    yield test_user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()


@pytest.fixture
def test_city1():
    test_city = UserFavouriteCities(user_id=1, city_name="Warszawa")
    db = TestingSessionLocal()
    db.add(test_city)
    db.commit()
    yield test_city
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM user_favourite_cities"))
        connection.commit()


@pytest.fixture
def test_city2():
    test_city = UserFavouriteCities(user_id=1, city_name="Krakow")
    db = TestingSessionLocal()
    db.add(test_city)
    db.commit()
    yield test_city
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM user_favourite_cities"))
        connection.commit()
