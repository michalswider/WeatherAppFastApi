from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker
from starlette import status

from ..database import Base
from ..models import User, UserFavouriteCities, WeatherCache
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


@pytest.fixture
def test_city3():
    test_city = UserFavouriteCities(user_id=1, city_name="Lublin")
    db = TestingSessionLocal()
    db.add(test_city)
    db.commit()
    yield test_city
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM user_favourite_cities"))
        connection.commit()


@pytest.fixture
def test_weather_data1():
    current_time = datetime.now().date()
    test_data = WeatherCache(
        city="Warszawa",
        weather_data={
            "coord": {"lon": 21.0118, "lat": 52.2298},
            "weather": [
                {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
            ],
            "base": "stations",
            "main": {
                "temp": 3.86,
                "feels_like": 1.45,
                "temp_min": 2.34,
                "temp_max": 5.4,
                "pressure": 1019,
                "humidity": 86,
                "sea_level": 1019,
                "grnd_level": 1007,
            },
            "visibility": 10000,
            "wind": {"speed": 2.61, "deg": 204, "gust": 7.63},
            "clouds": {"all": 6},
            "dt": 1738222260,
            "sys": {
                "type": 2,
                "id": 2032856,
                "country": "PL",
                "sunrise": 1738217987,
                "sunset": 1738250313,
            },
            "timezone": 3600,
            "id": 756135,
            "name": "Warsaw",
            "cod": 200,
        },
        query_date=current_time,
    )
    db = TestingSessionLocal()
    db.add(test_data)
    db.commit()
    yield test_data
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM weather_cache"))
        connection.commit()


mock_weather_response = {
    "coord": {"lon": 23, "lat": 51},
    "weather": [
        {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
    ],
    "base": "stations",
    "main": {
        "temp": 4.6,
        "feels_like": 2.32,
        "temp_min": 4.6,
        "temp_max": 4.6,
        "pressure": 1021,
        "humidity": 82,
        "sea_level": 1021,
        "grnd_level": 993,
    },
    "visibility": 10000,
    "wind": {"speed": 2.62, "deg": 199, "gust": 5.94},
    "clouds": {"all": 0},
    "dt": 1738223895,
    "sys": {"country": "PL", "sunrise": 1738217257, "sunset": 1738250088},
    "timezone": 3600,
    "id": 858785,
    "name": "Lublin Voivodeship",
    "cod": 200,
}


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = status.HTTP_200_OK
        mock_get.return_value.json.return_value = mock_weather_response
        yield mock_get
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM weather_cache"))
        connection.commit()


@pytest.fixture
def mock_requests_error_404():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=status.HTTP_404_NOT_FOUND)
        )

        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_requests_error_400():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=status.HTTP_400_BAD_REQUEST)
        )

        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_requests_connection_error():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.ConnectionError

        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_requests_timeout_error():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.Timeout

        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_requests_network_error():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.RequestException
        )

        mock_get.return_value = mock_response
        yield mock_get
