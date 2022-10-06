#!/usr/bin/env python3

"""Agnosis filter bubble breaker"""

import os
from flask import Flask

# TODO Initialize DB


def create_app():
    """Initialize the application"""
    app = Flask(__name__, instance_relative_config=False)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET")

    # TODO Initialize database, get DB uri, etc;

    with app.app_context():

        from . import routes

        # TODO db.create_all()

        return app
