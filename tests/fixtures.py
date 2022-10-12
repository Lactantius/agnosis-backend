import os

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.db import init_driver, close_driver


@pytest.fixture()
def app() -> Flask:
    app = create_app()

    app.config["TESTING"] = True
    app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]
    app.config["WTF_CSRF_ENABLED"] = False

    return app
