from fastapi.testclient import TestClient
from starlette import status

from ..main import app
from ..routers.auth import get_current_user, get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_show_user_detail(test_user1):
    response = client.get("/user_panel/detail")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "first_name": "test",
        "last_name": "test",
        "username": "test",
        "role": "user",
    }


def test_reset_password(test_user1):
    request_data = {
        "old_password": "test1234",
        "new_password": "qwerty1234",
    }
    response = client.put("/user_panel/reset_password", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_reset_password_error(test_user1):
    request_data = {
        "old_password": "testtesttest",
        "new_password": "qwerty1234",
    }
    response = client.put("/user_panel/reset_password", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Error on password change"}
