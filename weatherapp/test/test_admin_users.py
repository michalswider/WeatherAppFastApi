from fastapi.testclient import TestClient
from starlette import status

from ..main import app
from ..routers.auth import get_current_user, get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_add_user(test_user1):
    request_data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "username": "j_kowalski",
        "password": "test1234",
        "role": "user",
    }

    response = client.post("/users/add", json=request_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "User created successfully."}
    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 2).first()
    assert model.first_name == request_data["first_name"]
    assert model.last_name == request_data["last_name"]
    assert model.username == request_data["username"]
    assert model.role == request_data["role"]


def test_add_user_username_exist(test_user1):
    request_data = {
        "first_name": "test",
        "last_name": "test",
        "username": "test",
        "password": "test1234",
        "role": "user",
    }

    response = client.post("/users/add", json=request_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Username already exists"}


def test_add_user_invalid_role(test_user1):
    request_data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "username": "j_kowalski",
        "password": "test1234",
        "role": "test",
    }

    response = client.post("/users/add", json=request_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Invalid status: test. Allowed status are 'user', 'admin'."
    }


def test_show_users(test_user1):
    response = client.get("/users/show")

    users = response.json()
    user_data = next((user for user in users if user["username"] == "test"), None)
    assert response.status_code == status.HTTP_200_OK
    assert len(users) > 0
    assert user_data is not None
    assert user_data["id"] == 1
    assert user_data["first_name"] == "test"
    assert user_data["last_name"] == "test"
    assert user_data["username"] == "test"
    assert user_data["role"] == "user"


def test_show_user_without_users():
    response = client.get("/users/show")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_edit_user(test_user1):
    request_data = {"first_name": "Johny", "last_name": "Bravo", "username": "j_bravo"}
    response = client.put("/users/update/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 1).first()
    assert model.first_name == request_data["first_name"]
    assert model.last_name == request_data["last_name"]
    assert model.username == request_data["username"]


def test_edit_user_id_user_not_found():
    request_data = {"first_name": "Johny", "last_name": "Bravo", "username": "j_bravo"}
    response = client.put("/users/update/999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_edit_user_username_already_exist(test_user1, test_user2):
    request_data = {"username": "test"}
    response = client.put("/users/update/2", json=request_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Username already exists"}


def test_edit_user_invalid_role(test_user1):
    request_data = {"role": "test"}
    response = client.put("/users/update/1", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Invalid status: test. Allowed status are 'user', 'admin'."
    }


def test_delete_user(test_user1):
    response = client.delete("/users/delete/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 1).first()
    assert model is None


def test_delete_user_user_id_not_found():
    response = client.delete("/users/delete/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}
