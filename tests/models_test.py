import pytest

from app.db import get_driver
from app.models.user import register, authenticate
from app.models.source import add_source

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

            assert user["userId"] is not None
            assert user["email"] == test_user["email"]
            assert user["token"] is not None

            in_db = authenticate(driver, user["email"], test_user["password"])

            assert in_db["username"] == user["username"]


def test_none_returned_if_username_or_password_not_unique(app):
    """Should not be able to make a user with an old username or password"""
    with app.app_context():
        with get_driver() as driver:

            user = register(
                driver, test_user["email"], test_user["password"], test_user["username"]
            )

            # assert bad_username is None
            with pytest.raises(Exception):
                register(
                    driver, "bob@bob.com", test_user["password"], test_user["username"]
                )

            with pytest.raises(Exception):
                register(driver, test_user["email"], test_user["password"], "bob")


def test_can_authenticate_user(app):
    """Checks if user1 can be authenticated"""
    with app.app_context():
        with get_driver() as driver:

            user = authenticate(driver, "user1@user1.com", "password1")

            assert user["username"] == "user1"


def test_can_add_source(app):
    with app.app_context():
        with get_driver() as driver:

            source = add_source(driver, "Test Source")

            assert source["name"] == "Test Source"
