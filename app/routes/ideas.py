""" Routes for ideas """

from flask import Blueprint, jsonify, request, current_app
from flask.wrappers import Response
from flask_jwt_extended import jwt_required, get_jwt

from app.models.idea import (
    add_idea,
    random_idea,
    random_unseen_idea,
    get_agreeable_idea,
    get_disagreeable_idea,
    get_ideas,
    like_idea,
    dislike_idea,
    get_seen_ideas,
    get_idea_with_reaction,
    get_idea_with_all_reactions,
    delete_idea,
    get_posted_ideas,
    get_all_seen_ideas_with_user_and_aggregate_reactions,
)

ideas = Blueprint("ideas", __name__, url_prefix="/api/ideas")


@ideas.post("/")
@jwt_required()
def post_idea() -> tuple[Response, int]:
    """Post a new idea"""

    claims = get_jwt()
    user_id = claims.get("userId", None)

    data = request.get_json()
    url = data.get("url", None)
    description = data.get("description", None)
    source_id = data.get("sourceId", None)

    idea = add_idea(
        current_app.driver,
        {
            "url": url,
            "description": description,
            "user_id": user_id,
            "source_id": source_id,
        },
    )

    return (jsonify(idea=idea), 201)


@ideas.get("/random")
def get_idea() -> tuple[Response, int]:
    """Get an idea from the database"""

    idea = random_idea(current_app.driver, "fake")

    return (jsonify(idea=idea), 200)


@ideas.get("/random-unseen")
@jwt_required()
def get_unseen_idea() -> tuple[Response, int]:
    """Get a random idea that the user has not yet seen"""

    claims = get_jwt()
    user_id = claims.get("userId", None)

    idea = random_unseen_idea(current_app.driver, user_id)

    if idea is None:
        return (jsonify(error="We are all out of idea you haven't seen before."), 404)

    return (jsonify(idea=idea[0]), 200)


@ideas.get("/disagreeable")
@jwt_required()
def disagreeable_idea():
    """Get an idea that the user should be interested in but disagree with"""

    claims = get_jwt()
    user_id = claims.get("userId", None)

    idea = get_disagreeable_idea(current_app.driver, user_id)

    if idea is None:
        return (jsonify(error="We are all out of ideas for you to disagree with."), 404)

    return (jsonify(idea=idea[0]), 200)


@ideas.get("/agreeable")
@jwt_required()
def agreeable_idea():
    """Get an idea that the user should be interested in but disagree with"""

    claims = get_jwt()
    user_id = claims.get("userId", None)

    idea = get_agreeable_idea(current_app.driver, user_id)

    if idea is None:
        return (jsonify(error="We are all out of nice ideas."), 404)

    return (jsonify(idea=idea[0]), 200)


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


@ideas.get("/viewed-with-relationships")
@jwt_required()
def viewed_ideas_with_relationships():

    claims = get_jwt()
    user_id = claims.get("userId", None)

    ideas = get_all_seen_ideas_with_user_and_aggregate_reactions(
        current_app.driver, user_id
    )

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


@ideas.delete("/<string:idea_id>")
@jwt_required()
def delete_single_idea(idea_id):

    claims = get_jwt()
    user_id = claims.get("userId", None)

    user_id = claims.get("userId", None)
    query_res = delete_idea(current_app.driver, idea_id, user_id)

    return jsonify({"deleted": query_res})


@ideas.get("/user/<string:user_id>")
@jwt_required()
def posted_by_user(user_id):
    """Get ideas posted by a user"""

    claims = get_jwt()
    current_user = claims.get("userId", None)
    if current_user != user_id:
        return (jsonify(error="You are not authorized to view this resource"), 403)

    ideas = get_posted_ideas(current_app.driver, user_id)
    return jsonify(ideas=ideas)
