"""Routes for registration and authentication"""

from flask import Blueprint, jsonify, request, current_app

from app.models.user import register, authenticate
from app.exceptions.validation_exception import ValidationException

auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth.post("/signup")
def signup():
    form_data = request.get_json()

    email = form_data["email"]
    password = form_data["password"]
    username = form_data["username"]

    try:
        user = register(current_app.driver, email, password, username)
    except ValidationException as err:
        return (jsonify(error=err.message), 401)

    return (jsonify(user=user), 201)


@auth.post("/login")
def login():
    form_data = request.get_json()

    email = form_data["email"]
    password = form_data["password"]

    user = authenticate(current_app.driver, email, password)

    if user is False:
        return "Unauthorized", 401

    return jsonify(user)
