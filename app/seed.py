"""Setup database"""

from functools import partial
import random
from neo4j_backup import Extractor, Importer
from faker import Faker

from .fake_data import users, sources, ideas
from .types import RegistrationData, IdeaData
from .models.user import register
from .models.source import add_source
from .models.idea import add_idea, like_idea, dislike_idea

fake = Faker()
Faker.seed(0)


def clear_db(tx):
    """Delete all from db"""
    tx.run("MATCH (n) DETACH DELETE n")


def set_db_properties(driver):
    def constraints(tx):
        tx.run(
            "CREATE CONSTRAINT unique_email IF NOT EXISTS FOR (user:User) REQUIRE user.email IS UNIQUE"
        )
        tx.run(
            "CREATE CONSTRAINT unique_username IF NOT EXISTS FOR (user:User) REQUIRE user.username IS UNIQUE"
        )
        tx.run(
            "CREATE CONSTRAINT unique_source_name IF NOT EXISTS FOR (source:Source) REQUIRE source.name IS UNIQUE"
        )

    def indices(tx):
        tx.run(
            "CREATE FULLTEXT INDEX urlsAndDescriptions IF NOT EXISTS FOR (i:Idea) ON EACH [i.url, i.description]"
        )

    with driver.session() as session:
        session.execute_write(constraints)
        session.execute_write(indices)


def seed_db(driver):
    """Set initial values for db"""
    random.seed(0)
    user1 = register(
        driver,
        {"email": "user1@user1.com", "password": "password1", "username": "user1"},
    )
    user2 = register(
        driver,
        {"email": "user2@user2.com", "password": "password2", "username": "user2"},
    )
    source1 = add_source(driver, {"name": "Scott Alexander"})
    source2 = add_source(driver, {"name": "Ross Douthat"})
    idea1 = add_idea(
        driver,
        {
            "url": "https://slatestarcodex.com/2014/04/22/right-is-the-new-left/",
            "user_id": user1["userId"],
            "source_id": source1["sourceId"],
            "description": "A theory of social change using cellular automata",
        },
    )
    idea2 = add_idea(
        driver,
        {
            "url": "https://www.nytimes.com/2020/02/07/opinion/sunday/western-society-decadence.html",
            "user_id": user2["userId"],
            "source_id": source2["sourceId"],
            "description": "Western society is more decadent than you think",
        },
    )
    print(users)
    registered = list(map(partial(register, driver), users))
    db_sources = list(map(partial(add_source, driver), sources))

    def add_rand_user_and_source(idea: dict) -> IdeaData:
        return {
            **idea,
            "user_id": random.choice(registered)["userId"],
            "source_id": random.choice(db_sources)["sourceId"],
        }

    db_ready_ideas = map(add_rand_user_and_source, ideas)
    db_ideas = list(map(partial(add_idea, driver), db_ready_ideas))

    # This will overwrite some stuff, but that's fine for now.
    for user in registered:
        for _ in range(10):
            if random.choice([True, False]):
                like_idea(
                    driver,
                    user["userId"],
                    random.choice(db_ideas)["ideaId"],
                    random.randint(-3, 3),
                )
            else:
                dislike_idea(driver, user["userId"], random.choice(db_ideas)["ideaId"])


def dump_db(driver):
    extractor = Extractor(
        project_dir="dev_data",
        driver=driver,
        database="neo4j",
        input_yes=True,
        compress=True,
    )
    extractor.extract_data()


def import_dev_data(driver):
    importer = Importer(
        project_dir="dev_data", driver=driver, database="neo4j", input_yes=True
    )
    importer.import_data()


def reset_db(driver):
    """Clear and seed db"""
    with driver.session() as session:
        session.execute_write(clear_db)
        seed_db(driver)
