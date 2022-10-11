import os

import pytest

from app import create_app
from app.db import init_driver, close_driver


@pytest.fixture
def app():
    app = create_app()

    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            init_driver(
                os.getenv("NEO4J_URI"),
                os.getenv("NEO4J_USERNAME"),
                os.getenv("NEO4J_PASSWORD"),
            )
        yield client
