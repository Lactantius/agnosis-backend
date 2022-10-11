from .models.user import register


def clear_db(tx):
    """Delete all from db"""
    tx.run("MATCH (n) DETACH DELETE n")


def set_constraints(driver):
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

    with driver.session() as session:
        session.execute_write(constraints)


def seed_db(driver):
    """Set initial values for db"""
    user1 = register(driver, "user1@user1.com", "password1", "user1")
    user2 = register(driver, "user2@user2.com", "password2", "user2")


def reset_db(driver):
    """Clear and seed db"""
    with driver.session() as session:
        session.execute_write(clear_db)
        seed_db(driver)
