""" Routes for ideas """

from flask import Blueprint, jsonify, request, current_app
from flask.wrappers import Response
from flask_jwt_extended import jwt_required, get_jwt

from app.models.idea import (
    random_idea,
    get_agreeable_idea,
    get_disagreeable_idea,
    get_ideas,
    like_idea,
    dislike_idea,
    get_seen_ideas,
    get_idea_with_reaction,
    get_idea_with_all_reactions,
)

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

    return (jsonify(idea=idea), 200)


@ideas.get("/disagreeable")
@jwt_required()
def disagreeable_idea():
    """Get an idea that the user should be interested in but disagree with"""

    claims = get_jwt()
    user_id = claims.get("userId", None)

    idea = get_disagreeable_idea(current_app.driver, user_id)

    return (jsonify(idea=idea), 200)


@ideas.get("/agreeable")
@jwt_required()
def agreeable_idea():
    """Get an idea that the user should be interested in but disagree with"""

    claims = get_jwt()
    user_id = claims.get("userId", None)

    idea = get_agreeable_idea(current_app.driver, user_id)

    return (jsonify(idea=idea), 200)


@ideas.post("/<string:idea_id>/react")
@jwt_required()
def react_to_idea(idea_id):

    claims = get_jwt()
    user_id = claims.get("userId", None)

    data = request.get_json()
    type = data["type"]

    if type == "like":
        reaction = like_idea(current_app.driver, user_id, idea_id, data["agreement"])
    else:
        reaction = dislike_idea(current_app.driver, user_id, idea_id)

    return (jsonify(reaction=reaction), 200)


@ideas.get("/viewed")
@jwt_required()
def viewed_ideas():
    claims = get_jwt()
    user_id = claims.get("userId", None)

    ideas = get_seen_ideas(current_app.driver, user_id)

    return jsonify(ideas=ideas)


@ideas.get("/<string:idea_id>")
@jwt_required()
def idea_details(idea_id):

    claims = get_jwt()
    user_id = claims.get("userId", None)

    idea = get_idea_with_reaction(current_app.driver, idea_id, user_id)
    return jsonify(idea=idea)


@ideas.get("/<string:idea_id>/reactions")
@jwt_required()
def idea_reactions(idea_id):

    idea = get_idea_with_all_reactions(current_app.driver, idea_id)
    return jsonify(idea=idea)
