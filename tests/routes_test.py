"""Test API routes"""

from flask import request, session
from flask.testing import FlaskClient
import pytest

from .fixtures import app
from app.routes.ideas import get_idea


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()


##############################################################################
# Auth
#


def test_can_signup(client: FlaskClient) -> None:
    """Can one sign up for a new account?"""

    with client:
        res = client.post(
            "/api/users/signup",
            json={
                "email": "apitest@apitest.com",
                "password": "apitest1",
                "username": "apitest1",
            },
        )
        assert res.status_code == 201
        assert res.json["user"]["email"] == "apitest@apitest.com"


def test_error_message_if_username_or_email_not_unique(client: FlaskClient) -> None:
    """Will correct error message show?"""

    with client:
        bad_username = client.post(
            "/api/users/signup",
            json={
                "email": "apitest@apitest.com",
                "password": "apitest1",
                "username": "user1",
            },
        )
        assert bad_username.status_code == 409
        assert "already exists" in bad_username.json["error"]

        bad_email = client.post(
            "/api/users/signup",
            json={
                "email": "user1@user1.com",
                "password": "apitest1",
                "username": "apitest1",
            },
        )
        assert bad_email.status_code == 409
        assert "already exists" in bad_email.json["error"]


def test_can_login(client: FlaskClient) -> None:
    """Can one login?"""

    with client:
        res = client.post(
            "/api/users/login",
            json={
                "email": "user1@user1.com",
                "password": "password1",
            },
        )
        assert res.status_code == 200
        assert res.json["user"]["email"] == "user1@user1.com"


def test_cannot_login_with_invalid_credentials(client: FlaskClient) -> None:
    """Is login refused with bad credentials?"""

    with client:
        bad_password = client.post(
            "/api/users/login",
            json={"email": "user1@user1.com", "password": "bad_password"},
        )
        assert bad_password.status_code == 401
        assert bad_password.json["error"] == "Invalid username or password"

    with client:
        bad_email = client.post(
            "/api/users/login",
            json={"email": "invalid@invalid.com", "password": "password1"},
        )
        assert bad_email.status_code == 401
        assert bad_email.json["error"] == "Invalid username or password"


##############################################################################
# User Info
#


def test_can_view_user_info(client: FlaskClient) -> None:
    with client:
        user = client.post(
            "/api/users/login",
            json={
                "email": "user1@user1.com",
                "password": "password1",
            },
        ).json
        user_id = user["user"]["sub"]
        token = user["user"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        res = client.get(f"/api/users/{user_id}", headers=headers)

        assert res.status_code == 200
        assert res.json["user"]["username"] == "user1"


##############################################################################
# Ideas
#


def test_get_random_idea(client: FlaskClient) -> None:
    """Can one get a random idea?"""

    with client:

        res = client.get("/api/ideas/random")

        assert res.status_code == 200
        assert res.json["idea"]["url"] is not None
