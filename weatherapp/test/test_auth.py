from datetime import timedelta

from jose import jwt

from ..main import app
from ..routers.auth import (ALGORITHM, SECRET_KEY, authenticate_user,
                            create_access_token, get_db)
from .utils import *

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user1):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user1.username, "test1234", db)
    assert authenticated_user is not False
    assert authenticated_user.username == test_user1.username


def test_authenticate_user_wrong_username():
    db = TestingSessionLocal()
    authenticated_user = authenticate_user("wrong_username", "test1234", db)
    assert authenticated_user is False


def test_authenticate_user_wrong_password(test_user1):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user1.username, "wrong_password", db)
    assert authenticated_user is False


def test_create_access_token():
    username = "testtest"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)
    token = create_access_token(username, user_id, role, expires_delta)
    decoded_token = jwt.decode(
        token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False}
    )
    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["role"] == role
