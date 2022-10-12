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


def test_get_random_idea(client):
    """Can one get a random idea?"""

    with client:

        res = client.get("/api/ideas/random")

        assert res.status_code == 200
        assert res.json["idea"]["url"] is not None
