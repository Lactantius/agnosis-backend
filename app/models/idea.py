"""Idea model"""

from datetime import datetime
from flask import current_app
from neo4j.exceptions import ConstraintError

from app.types import IdeaData


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


def create_idea(tx, data: IdeaData):
    """Transaction function for adding a new idea to the db"""
    return tx.run(
        """
        MATCH (u:User {userId: $user_id})
        MATCH (s:Source {sourceId: $source_id})
        MERGE (i:Idea {url: $url, description: $description})<-[f:AUTHORED]-(s)
        ON CREATE SET i.createdAt = datetime(), i.ideaId = randomUuid()
        RETURN i {
            .*
        } AS idea
        """,
        url=data["url"],
        user_id=data["user_id"],
        source_id=data["source_id"],
        description=data["description"],
    ).single()


##############################################################################
# Main functions
#


def all_ideas(driver, sort, order, limit=6, skip=0):
    """Get all ideas with optional paging"""

    with driver.session() as session:
        return session.execute_read(get_ideas, sort, order, limit, skip)


def add_idea(driver, data: IdeaData):
    """Add a new idea to the database"""

    with driver.session() as session:
        return session.execute_write(create_idea, data)["idea"]


def random_idea(driver, user_id):
    with driver.session() as session:
        return session.execute_read(
            lambda tx: tx.run(
                """
                MATCH (i:Idea)
                RETURN i {
                    .*,
                    createdAt: toString(i.createdAt)
                }
                ORDER BY rand()
                LIMIT 1
                """
            ).single()
        )["i"]


def get_disagreeable_idea(driver, user_id):
    with driver.session() as session:
        result = session.execute_read(
            lambda tx: tx.run(
                """
                MATCH p = (:User { userId: $user_id })-[:LIKES]->(:Idea)<-[:LIKES]-(:User)-[:LIKES]->(i:Idea)
                WITH *, relationships(p) as likes
                WITH *, reduce(acc = 1, like IN likes | acc * like.agreement) AS agree
                RETURN i, sum(agree) AS agreement
                ORDER BY agreement
                LIMIT 1
                """,
                user_id=user_id,
            ).single()
        )
        return result.values("i", "agreement")


def get_agreeable_idea(driver, user_id):
    with driver.session() as session:
        result = session.execute_read(
            lambda tx: tx.run(
                """
                MATCH p = (:User { userId: $user_id })-[:LIKES]->(:Idea)<-[:LIKES]-(:User)-[:LIKES]->(i:Idea)
                WITH *, relationships(p) as likes
                WITH *, reduce(acc = 1, like IN likes | acc * like.agreement) AS agree
                RETURN i, sum(agree) AS agreement
                ORDER BY agreement DESC
                LIMIT 1
                """,
                user_id=user_id,
            ).single()
        )

        return result.values("i", "agreement")


def search_ideas(driver, search_str: str):
    """Search an idea by url and description"""

    def search(tx, search_str: str):
        result = tx.run(
            """
            CALL db.index.fulltext.queryNodes("urlsAndDescriptions", $search_str) YIELD node, score
            RETURN node.ideaId AS id, node.url AS url, node.description AS description, score
            """,
            search_str=search_str,
        ).values("id", "url", "description")
        return [record for record in result]

    with driver.session() as session:
        return session.execute_read(search, search_str)


def like_idea(driver, user_id: str, idea_id: str, agreement: int) -> int:
    """
    Add a like relationship to an idea. If idea already liked, edits agreement level.
    If idea is disliked, deleted dislike relationship
    """

    def like(tx, user_id: str, idea_id: str, agreement: int) -> int:
        result = tx.run(
            """
            MATCH (u:User {userId: $user_id})
            MATCH (i:Idea {ideaId: $idea_id})
            OPTIONAL MATCH (u)-[d:DISLIKES]->(i)
            DELETE d
            MERGE (u)-[l:LIKES]->(i)
            SET l.agreement=$agreement
            RETURN l.agreement as agreement
            """,
            user_id=user_id,
            idea_id=idea_id,
            agreement=agreement,
        ).single()
        return result["agreement"]

    with driver.session() as session:
        return session.execute_write(like, user_id, idea_id, agreement)


def dislike_idea(driver, user_id: str, idea_id: str):
    """Add a like relationship to an idea. If idea already liked, deletes like relationship"""

    def dislike(tx, user_id: str, idea_id: str):
        result = tx.run(
            """
            MATCH (u:User {userId: $user_id})
            MATCH (i:Idea {ideaId: $idea_id})
            OPTIONAL MATCH (u)-[l:LIKES]->(i)
            DELETE l
            MERGE (u)-[d:DISLIKES]->(i)
            RETURN d
            """,
            user_id=user_id,
            idea_id=idea_id,
        ).single()
        return result["d"].type

    with driver.session() as session:
        return session.execute_write(dislike, user_id, idea_id)


##############################################################################
# Helper functions
#
