"""Routes for registration and authentication"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt

from app.models.user import register, authenticate, find_user
from app.exceptions.validation_exception import ValidationException

users = Blueprint("users", __name__, url_prefix="/api/users")


##############################################################################
# Authentication
#


@users.post("/signup")
def signup():
    data = request.get_json()

    email = data["email"]
    password = data["password"]
    username = data["username"]

    try:
        user = register(current_app.driver, email, password, username)
    except ValidationException as err:
        return (jsonify(error=err.message), 409)

    return (jsonify(user=user), 201)


@users.post("/login")
def login():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    user = authenticate(current_app.driver, email, password)

    if user is False:
        return (jsonify(error="Invalid username or password"), 401)

    return (jsonify(user=user), 200)


##############################################################################
# User info
#


@users.get("/<string:user_id>")
@jwt_required()
def get_user(user_id):

    claims = get_jwt()
    current_user = claims.get("userId", None)
    if current_user != user_id:
        return (jsonify(error="You are not authorized to view this resource"), 403)

    user = find_user(current_app.driver, claims.get("email"))
    without_pass = {key: value for key, value in user.items() if key != "password"}

    return (jsonify(user=without_pass), 200)
