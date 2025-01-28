from fastapi.testclient import TestClient
from starlette import status

from ..main import app
from ..routers.auth import get_current_user, get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_add_favourite_city(test_city1):
    request_data = {"city": "Poznan"}
    response = client.post("/favourite/add", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "City added successfully."}
    db = TestingSessionLocal()
    model = (
        db.query(UserFavouriteCities)
        .filter(UserFavouriteCities.user_id == 1, UserFavouriteCities.id == 2)
        .first()
    )
    assert model is not None
    assert model.city_name == request_data["city"]


def test_add_favourite_city_name_exist(test_city1):
    request_data = {"city": "Warszawa"}
    response = client.post("/favourite/add", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Favourite city: Warszawa already exist."}


def test_show_favourite_cities(test_city1):
    response = client.get("/favourite/show")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"id": 1, "city": "Warszawa"}]


def test_show_favourite_cities_without_cities():
    response = client.get("/favourite/show")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Cities not found"}


def test_edit_favourite_city(test_city1):
    request_data = {"city": "Poznan"}
    response = client.put("/favourite/update/1", json=request_data)
    db = TestingSessionLocal()
    model = db.query(UserFavouriteCities).filter(UserFavouriteCities.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model.city_name == request_data["city"]


def test_edit_favourite_city_name_exist(test_city1, test_city2):
    request_data = {"city": "Warszawa"}
    response = client.put("/favourite/update/2", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Favourite city: Warszawa already exist."}


def test_edit_favourite_city_not_exist():
    request_data = {"city": "Warszawa"}
    response = client.put("/favourite/update/999", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "City not exist"}


def test_delete_favourite_city(test_city1):
    response = client.delete("/favourite/delete/1")
    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert model is None


def test_delete_favourite_city_not_exist():
    response = client.delete("/favourite/delete/999")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "City not exist"}
