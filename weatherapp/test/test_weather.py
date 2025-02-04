from fastapi.testclient import TestClient

from ..main import app
from ..routers.auth import get_current_user, get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_weather_from_cache(test_weather_data1):
    response = client.get("/weather/warszawa")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "City": "Warszawa",
        "Temperature": 4,
        "Minimal temperature": 2,
        "Maximal temperature": 5,
        "Weather conditions": "clear sky",
    }


def test_weather_from_api(mock_requests_get):
    response = client.get("/weather/lublin")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "City": "Lublin",
        "Temperature": 5,
        "Minimal temperature": 5,
        "Maximal temperature": 5,
        "Weather conditions": "clear sky",
    }


def test_get_weather_city_not_found(mock_requests_error_404):
    response = client.get("/weather/test")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "City not found"}


def test_get_weather_missing_city_name_or_missing_param(mock_requests_error_400):
    response = client.get("/weather/test")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Invalid city name or missing parameters in the request."
    }


def test_get_weather_connection_error(mock_requests_connection_error):
    response = client.get("/weather/test")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Connection error"}


def test_get_weather_timeout_error(mock_requests_timeout_error):
    response = client.get("/weather/test")
    assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
    assert response.json() == {"detail": "Request timeout"}


def test_get_weather_network_error(mock_requests_network_error):
    response = client.get("/weather/test")
    assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT


def test_get_weather_for_favourite_cities(
    test_city1, test_city3, test_weather_data1, mock_requests_get
):
    response = client.get("/weather/favourite/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "City": "Warszawa",
            "Temperature": 4,
            "Minimal temperature": 2,
            "Maximal temperature": 5,
            "Weather conditions": "clear sky",
        },
        {
            "City": "Lublin",
            "Temperature": 5,
            "Minimal temperature": 5,
            "Maximal temperature": 5,
            "Weather conditions": "clear sky",
        },
    ]


def test_get_weather_for_favourite_cities_not_found():
    response = client.get("/weather/favourite/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Cities not found"}


def test_get_weather_for_favourite_cities_one_city_not_found(
    test_city1, test_city3, test_weather_data1, mock_requests_error_404
):
    response = client.get("/weather/favourite/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "City": "Warszawa",
            "Temperature": 4,
            "Minimal temperature": 2,
            "Maximal temperature": 5,
            "Weather conditions": "clear sky",
        },
        {"city": "Lublin", "error": "Not Found", "details": "City not found"},
    ]


def test_get_weather_for_favourite_cities_one_missing_city_name_or_missing_param(
    test_city1, test_city3, test_weather_data1, mock_requests_error_400
):
    response = client.get("/weather/favourite/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "City": "Warszawa",
            "Temperature": 4,
            "Minimal temperature": 2,
            "Maximal temperature": 5,
            "Weather conditions": "clear sky",
        },
        {
            "city": "Lublin",
            "error": "Invalid error",
            "details": "Invalid city name or missing parameters in the request.",
        },
    ]


def test_get_weather_for_favourite_cities_connection_error(
    test_city1, test_city3, mock_requests_connection_error
):
    response = client.get("/weather/favourite/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "city": "Warszawa",
            "error": "Connection error",
            "details": "Connection error",
        },
        {
            "city": "Lublin",
            "error": "Connection error",
            "details": "Connection error",
        },
    ]


def test_get_weather_for_favourite_cities_one_city_timeout_error(
    test_city1, test_city3, test_weather_data1, mock_requests_timeout_error
):
    response = client.get("/weather/favourite/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "City": "Warszawa",
            "Temperature": 4,
            "Minimal temperature": 2,
            "Maximal temperature": 5,
            "Weather conditions": "clear sky",
        },
        {
            "city": "Lublin",
            "error": "Request timeout",
            "details": "Request timeout",
        },
    ]
