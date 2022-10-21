"""Source model"""

from flask import current_app
from neo4j.exceptions import ConstraintError

from app.types import SourceData


##############################################################################
# Transaction functions
#


def create_source(tx, data: SourceData):
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
            name=data["name"],
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


def add_source(driver, data: SourceData):
    """Register a new source"""

    try:
        with driver.session() as session:
            source = session.execute_write(create_source, data)

    except ConstraintError as err:
        # raise ValidationException(err.message, {"email": err.message})
        raise Exception

    return source


def all_sources(driver):
    """Get all sources"""

    def get_all(tx):
        result = tx.run(
            """
            MATCH (s:Source)
            RETURN s
            """
        )
        return [record["s"] for record in result]

    try:
        with driver.session() as session:
            sources = session.execute_read(get_all)

    except:
        raise Exception

    return sources


def find_source(driver, name):
    """Get a new source with its associated ideas"""

    try:
        with driver.session() as session:
            source = session.execute_read(get_source, name)

    except:
        # raise ValidationException(err.message, {"email": err.message})
        raise Exception

    return source


##############################################################################
# Helper functions
#
