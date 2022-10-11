"""Idea model"""

from datetime import datetime
from flask import current_app
from neo4j.exceptions import ConstraintError


##############################################################################
# Transaction functions
#


def get_ideas(tx, sort, order, limit, skip):
    """Transaction function for getting ideas"""

    cypher = """
        MATCH (i:Idea)
        WHERE exists(i.`{0}`)
        RETURN i {{
            .*
        }} AS idea
        ORDER BY i.`{0}` {1}
        SKIP $skip
        LIMIT $limit
    """.format(
        sort, order
    )

    result = tx.run(cypher, limit=limit, skip=skip)

    return [row.value("idea") for row in result]


def add_idea(
    tx, url: str, user_id: str, source_id: str, description: str, user_agreement: int
):
    """Transaction function for adding a new idea to the db"""
    return tx.run(
        """
        MATCH (u:User {user_id: $user_id})
        MATCH (s:Source {source_id: $source_id})
        MERGE (u)-[l:LIKES {agreement: $agreement}]->(i:Idea)<-[f:AUTHORED]-(s)
        ON CREATE SET u.createdAt = datetime()
        RETURN i {
            .*
        } AS idea
        """,
        user_id=user_id,
        source_id=source_id,
        agreement=user_agreement,
    ).single()


##############################################################################
# Main functions
#


def all_ideas(driver, sort, order, limit=6, skip=0):
    """Get all ideas with optional paging"""

    with driver.session() as session:
        return session.execute_read(get_ideas, sort, order, limit, skip)


def new_idea(
    driver,
    url: str,
    user_id: str,
    source_id: str,
    description: str,
    user_agreement: int,
):
    """Add a new idea to the database"""

    with driver.session() as session:
        return session.execute_write(
            add_idea, url, user_id, source_id, description, user_agreement
        )


##############################################################################
# Helper functions
#
