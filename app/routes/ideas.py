""" Routes for ideas """

from flask import Blueprint, jsonify, request, current_app
from flask.wrappers import Response

from app.models.idea import random_idea

ideas = Blueprint("ideas", __name__, url_prefix="/api/ideas")


@ideas.get("/random")
def get_idea() -> tuple[Response, int]:
    """Get an idea from the database"""

    # idea = {
    #     "id": 1,
    #     "text": "An idea",
    #     "url": "https://example.com/idea",
    #     "source": "Example news source",
    # }
    idea = random_idea(current_app.driver, "fake")
    print(idea)

    return (jsonify(idea=idea), 200)
