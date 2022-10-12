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
# Ideas
#


def test_can_signup(client: FlaskClient):
    """Can one sign up for a new account?"""

    with client:
        res = client.post(
            "/api/auth/signup",
            json={
                "email": "apitest@apitest.com",
                "password": "apitest1",
                "username": "apitest1",
            },
        )
        assert res.status_code == 201
        assert res.json["user"]["email"] == "apitest@apitest.com"


def test_error_message_if_username_or_email_not_unique(client: FlaskClient):
    """Will correct error message show?"""

    with client:
        bad_username = client.post(
            "/api/auth/signup",
            json={
                "email": "apitest@apitest.com",
                "password": "apitest1",
                "username": "user1",
            },
        )
        assert bad_username.status_code == 401
        assert "already exists" in bad_username.json["error"]

        bad_email = client.post(
            "/api/auth/signup",
            json={
                "email": "user1@user1.com",
                "password": "apitest1",
                "username": "apitest1",
            },
        )
        assert bad_email.status_code == 401
        assert "already exists" in bad_email.json["error"]


##############################################################################
# Ideas
#


def test_get_random_idea(client):
    """Can one get a random idea?"""

    with client:

        res = client.get("/api/ideas/random")

        assert res.status_code == 200
        assert res.json["idea"]["url"] is not None
