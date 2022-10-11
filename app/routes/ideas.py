""" Routes for ideas """

from flask import Blueprint, jsonify, request
from flask.wrappers import Response

ideas = Blueprint("ideas", __name__, url_prefix="/api/ideas")


@ideas.get("/random")
def get_idea() -> tuple[Response, int]:
    """Get an idea from the database"""

    idea = {
        "id": 1,
        "text": "An idea",
        "url": "https://example.com/idea",
        "source": "Example news source",
    }

    return (jsonify(idea=idea), 200)
