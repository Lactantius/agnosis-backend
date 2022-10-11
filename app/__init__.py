"""Agnosis filter bubble breaker"""

import os
from flask import Flask
from datetime import timedelta

from .routes.ideas import ideas
from .db import init_driver


def create_app():
    """Initialize the application"""

    app = Flask(__name__, instance_relative_config=False)

    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET", "secret"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET", "secret"),
        JWT_AUTH_HEADER_PREFIX="Bearer",
        JWT_VERIFY_CLAIMS="signature",
        JWT_EXPIRATION_DELTA=timedelta(360),
    )

    if os.getenv("FLASK_DEBUG") == "false":
        app.config.from_mapping(
            FLASK_DEBUG=False,
            NEO4J_URI=os.getenv("NEO4J_URI"),
            NEO4J_USERNAME=os.getenv("NEO4J_USERNAME"),
            NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD"),
            NEO4J_DATABASE=os.getenv("NEO4J_DATABASE"),
        )
    else:
        app.config.from_mapping(
            NEO4J_URI="neo4j://localhost:7687",
            NEO4J_USERNAME="neo4j",
            NEO4J_PASSWORD="test",
        ),

    with app.app_context():
        init_driver(
            app.config.get("NEO4J_URI"),
            app.config.get("NEO4J_USERNAME"),
            app.config.get("NEO4J_PASSWORD"),
        )
    # TODO db.create_all()

    app.register_blueprint(ideas)

    return app
