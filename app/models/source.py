"""Source model"""

from flask import current_app
from neo4j.exceptions import ConstraintError


##############################################################################
# Transaction functions
#


def create_source(tx, name):
    """Transaction function for adding a new source to the database"""
    return (
        tx.run(
            """
        CREATE (s:Source {
            sourceId: randomUuid(),
            name: $name
        })
        RETURN s
        """,
            name=name,
        )
        .single()
        .get("s")
    )


def get_source(tx, name):
    """Transaction function for getting a source and its ideas from the database"""
    # source = tx.run(
    #     """
    #     MATCH (s:Source {name: $name})-[a:AUTHORED]->(i:Idea)
    #     RETURN s, i {
    #         .*
    #     } AS idea
    #     """,
    #     name=name,
    # ).values("s", "idea")
    source = (
        tx.run(
            """
        MATCH (s:Source {name: $name})
        RETURN s
        """,
            name=name,
        )
        .single()
        .get("s")
    )

    return source


##############################################################################
# Main functions
#


def add_source(driver, name):
    """Register a new source"""

    try:
        with driver.session() as session:
            source = session.execute_write(create_source, name)

    except ConstraintError as err:
        # raise ValidationException(err.message, {"email": err.message})
        raise Exception

    return source


def find_source(driver, name):
    """Get a new source with its associated ideas"""

    try:
        with driver.session() as session:
            source = session.execute_read(get_source, name)

    except ConstraintError as err:
        # raise ValidationException(err.message, {"email": err.message})
        raise Exception

    return source


##############################################################################
# Helper functions
#
