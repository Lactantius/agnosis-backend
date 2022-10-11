import pytest

from app.db import get_driver
from app.models.user import register, authenticate

from .fixtures import app

test_user = {
    "email": "test@test.com",
    "password": "test_password",
    "username": "test_user",
}


def test_can_make_new_user(app):
    """Make a new user and checks that it was added to the db"""
    with app.app_context():
        with get_driver() as driver:

            user = register(
                driver, test_user["email"], test_user["password"], test_user["username"]
            )

            assert user["email"] == test_user["email"]

            in_db = authenticate(driver, user["email"], test_user["password"])

            assert in_db["username"] == user["username"]


def test_can_authenticate_user(app):
    """Checks if user1 can be authenticated"""
    with app.app_context():
        with get_driver() as driver:

            user = authenticate(driver, "user1@user1.com", "password1")

            assert user["username"] == "user1"
