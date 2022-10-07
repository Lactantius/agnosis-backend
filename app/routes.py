""" API Routes """

from functools import wraps
from uuid import UUID
from datetime import date, timedelta

from flask import current_app as app, Response, request, jsonify

##############################################################################
# Decorators
#


##############################################################################
# JSON API
#

@app.get("/ideas/random")
def get_idea() -> tuple[Response, int]:
    """Get an idea from the database"""

    idea = { "id": 1,
             "text": "This is an idea",
             "date": date(2022, 10, 06),
             "url": "https://example.com/idea",
             "source": "Example News Source"
            }

    return (jsonify(idea=idea)), 200)
