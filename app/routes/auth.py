"""Routes for registration and authentication"""

from flask import Blueprint, jsonify, request, current_app

from app.models.user import register, authenticate
from app.exceptions.validation_exception import ValidationException

auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth.post("/signup")
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


@auth.post("/login")
def login():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    user = authenticate(current_app.driver, email, password)

    if user is False:
        return (jsonify(error="Invalid username or password"), 401)

    return (jsonify(user=user), 200)
