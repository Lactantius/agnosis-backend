"""User model"""

from datetime import datetime
import jwt
import bcrypt
from flask import current_app
from neo4j.exceptions import ConstraintError

from app.exceptions.validation_exception import ValidationException

##############################################################################
# Transaction functions
#


def create_user(tx, email, encrypted, username):
    """Transaction function for adding a new user to the database"""
    return tx.run(
        """
        CREATE (u:User {
            userId: randomUuid(),
            email: $email,
            password: $encrypted,
            username: $username
        })
        RETURN u
        """,
        email=email,
        encrypted=encrypted,
        username=username,
    ).single()


def get_user(tx, email):
    """Transaction function for getting a user from the database"""
    user = tx.run(
        """
        MATCH (u:User {email: $email})
        RETURN u {
            .*
        }
        """,
        email=email,
    ).single()

    if user is None:
        return None

    return user.get("u")


##############################################################################
# Main functions
#


def register(driver, email, plain_password, username):
    """Register a new user"""

    encrypted = bcrypt.hashpw(plain_password.encode("utf8"), bcrypt.gensalt()).decode(
        "utf8"
    )

    try:
        with driver.session() as session:
            result = session.execute_write(create_user, email, encrypted, username)

    except ConstraintError as err:
        raise ValidationException(err.message, {"email": err.message})

    user = result["u"]

    payload = {
        "userId": user["userId"],
        "email": user["email"],
        "username": user["username"],
    }

    # Generate Token
    payload["token"] = generate_token(payload)

    return payload


def authenticate(driver, email, plain_password):
    """
    Find user by email address, hash password, and check against stored hash.
    If sucessful, return a dictionary containing the keys userId, email, username, and token.
    If unsuccessful, return False
    """

    with driver.session() as session:
        user = session.execute_read(get_user, email)

    if user is None:
        return False

    if (
        bcrypt.checkpw(plain_password.encode("utf-8"), user["password"].encode("utf-8"))
        is False
    ):
        return False

    payload = {
        "userId": user["userId"],
        "email": user["email"],
        "username": user["username"],
    }

    payload["token"] = generate_token(payload)

    return payload


def find_user(driver, email: str):
    with driver.session() as session:
        return session.execute_read(get_user, email)


##############################################################################
# Helper functions
#


def generate_token(payload):
    """Generate a JWT"""
    iat = datetime.utcnow()

    payload["sub"] = payload["userId"]
    payload["iat"] = iat
    payload["nbf"] = iat
    payload["exp"] = iat + current_app.config.get("JWT_EXPIRATION_DELTA")

    jwt_secret = current_app.config.get("JWT_SECRET_KEY")

    return jwt.encode(payload, jwt_secret, algorithm="HS256")  # .decode("ascii")


def decode_token(auth_token, jwt_secret):
    """Attempt to decode a JWT"""

    try:
        payload = jwt.decode(auth_token, jwt_secret)
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
