from .models.user import register
from .models.source import add_source
from .models.idea import add_idea


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
    user1 = register(driver, "user1@user1.com", "password1", "user1")
    user2 = register(driver, "user2@user2.com", "password2", "user2")
    source1 = add_source(driver, "Scott Alexander")
    source2 = add_source(driver, "Ross Douthat")
    idea1 = add_idea(
        driver,
        "https://slatestarcodex.com/2014/04/22/right-is-the-new-left/",
        user1["userId"],
        source1["sourceId"],
        "A theory of social change using cellular automata",
        1,
    )
    idea2 = add_idea(
        driver,
        "https://www.nytimes.com/2020/02/07/opinion/sunday/western-society-decadence.html",
        user2["userId"],
        source2["sourceId"],
        "Western society is more decadent than you think",
        -2,
    )


def reset_db(driver):
    """Clear and seed db"""
    with driver.session() as session:
        session.execute_write(clear_db)
        seed_db(driver)
