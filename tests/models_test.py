import pytest
from flask import Flask

from app.db import get_driver
from app.models.user import register, authenticate, find_user
from app.models.source import add_source, find_source, all_sources
from app.models.idea import add_idea, search_ideas, like_idea, dislike_idea


from .fixtures import app

test_user = {
    "email": "test@test.com",
    "password": "test_password",
    "username": "test_user",
}

test_idea = {
    "source": "Scott Alexander",
    "user": "user1",
    "url": "https://astralcodexten.substack.com/p/a-columbian-exchange",
    "description": "A fictional dialogue about the legitimacy of holidays",
}


def test_can_add_user(app):
    """Make a new user and checks that it was added to the db"""
    with app.app_context():
        with get_driver() as driver:

            user = register(
                driver, test_user["email"], test_user["password"], test_user["username"]
            )

            assert user["userId"] is not None
            assert user["email"] == test_user["email"]
            assert user["token"] is not None

            in_db = authenticate(driver, user["email"], test_user["password"])

            assert in_db["username"] == user["username"]


def test_none_returned_if_username_or_password_not_unique(app):
    """Should not be able to make a user with an old username or password"""
    with app.app_context():
        with get_driver() as driver:

            user = register(
                driver, test_user["email"], test_user["password"], test_user["username"]
            )

            # assert bad_username is None
            with pytest.raises(Exception):
                register(
                    driver, "bob@bob.com", test_user["password"], test_user["username"]
                )

            with pytest.raises(Exception):
                register(driver, test_user["email"], test_user["password"], "bob")


def test_can_authenticate_user(app):
    """Checks if user1 can be authenticated"""
    with app.app_context():
        with get_driver() as driver:

            user = authenticate(driver, "user1@user1.com", "password1")

            assert user["username"] == "user1"


def test_can_get_user_info(app):
    """Can user1 info be gathered"""
    with app.app_context():
        with get_driver() as driver:

            user = find_user(driver, "user1@user1.com")
            assert user["username"] == "user1"


def test_can_add_source(app):
    with app.app_context():
        with get_driver() as driver:

            source = add_source(driver, "Test Source")

            assert source["name"] == "Test Source"


def test_can_get_all_sources(app):
    with app.app_context():
        with get_driver() as driver:
            sources = all_sources(driver)

        assert len(sources) == 2
        assert sources[0]["name"] == "Scott Alexander"


def test_can_find_source(app):
    with app.app_context():
        with get_driver() as driver:
            source = find_source(driver, "Ross Douthat")

        assert source["name"] == "Ross Douthat"


def test_can_add_idea(app):
    with app.app_context():
        with get_driver() as driver:
            source_id = find_source(driver, "Scott Alexander")["sourceId"]
            user_id = find_user(driver, "user1@user1.com")["userId"]
            idea = add_idea(
                driver,
                test_idea["url"],
                user_id,
                source_id,
                test_idea["description"],
                2,
            )

        assert idea["description"] == test_idea["description"]


def test_can_search_ideas_by_description(app):
    with app.app_context():
        with get_driver() as driver:
            ideas = search_ideas(driver, "cellular")

        assert "automata" in ideas[0][2]


def test_can_like_idea(app):
    with app.app_context():
        with get_driver() as driver:
            user_id = find_user(driver, "user1@user1.com")["userId"]
            idea_id = search_ideas(driver, "cellular")[0][0]
            liked = like_idea(driver, user_id, idea_id, 2)

        assert liked == 2


def test_can_dislike_idea(app: Flask):
    with app.app_context():
        with get_driver() as driver:
            user_id = find_user(driver, "user1@user1.com")["userId"]
            idea_id = search_ideas(driver, "cellular")[0][0]
            disliked = dislike_idea(driver, user_id, idea_id)

        assert disliked == "DISLIKES"
