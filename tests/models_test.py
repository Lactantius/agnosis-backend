import pytest

from app.db import get_driver
from app.models.user import register, authenticate

from .fixtures import app

test_user = {
    "email": "test@test.com",
    "password": "test_password",
    "username": "test_user",
}


def test_make_new_user(app):
    with app.app_context():
        driver = get_driver()

        user = register(driver, "test@test.com", "test_password", "test_user")

        assert user["email"] == "test@test.com"


def test_get_user(app):
    with app.app_context():
        driver = get_driver()

        user = authenticate(driver, test_user["email"], test_user["password"])

        assert user["email"] == test_user["email"]
