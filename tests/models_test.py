import pytest

from app.db import get_driver
from app.models.user import register

from .fixtures import app


def test_make_new_user(app):
    with app.app_context():
        driver = get_driver()

        user = register(driver, "test@test.com", "test_password", "test_user")

        assert user["email"] == "test@test.com"
