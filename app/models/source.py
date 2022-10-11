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


def get_source(tx, source_id):
    """Transaction function for getting a source from the database"""
    source = tx.run(
        """
        MATCH (s:Source {sourceId: $source_id})
        RETURN s
        """,
        source_id=source_id,
    ).single()

    if source is None:
        return None

    return source.get("s")


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


##############################################################################
# Helper functions
#
