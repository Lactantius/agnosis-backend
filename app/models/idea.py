"""Idea model"""

from datetime import datetime
from flask import current_app
from neo4j.exceptions import ConstraintError

from app.types import IdeaData, Idea, IdeaWithAllReactions, IdeaWithAnonReactions


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
    if data.get("source_id", None):
        return tx.run(
            """
            MATCH (u:User {userId: $user_id})
            MATCH (s:Source {sourceId: $source_id})
            MERGE (u)-[:POSTED]->(i:Idea {url: $url, description: $description})<-[f:AUTHORED]-(s)
            ON CREATE SET i.createdAt = datetime(), i.ideaId = randomUuid()
            RETURN i {
                .*,
                createdAt: toString(i.createdAt)
            } AS idea
            """,
            url=data["url"],
            user_id=data["user_id"],
            source_id=data["source_id"],
            description=data["description"],
        ).single()

    result = tx.run(
        """
        MATCH (u:User {userId: $user_id})
        MERGE (u)-[:POSTED]->(i:Idea {url: $url, description: $description})
        ON CREATE SET i.createdAt = datetime(), i.ideaId = randomUuid()
        RETURN i {
            .*,
            createdAt: toString(i.createdAt)
        } AS idea
        """,
        url=data["url"],
        user_id=data["user_id"],
        description=data["description"],
    ).single()
    return result


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


def random_unseen_idea(driver, user_id):
    with driver.session() as session:
        return session.execute_read(
            lambda tx: tx.run(
                """
                MATCH (u:User {userId: $user_id})
                MATCH (i:Idea)
                WHERE NOT (u)-[]->(i)
                RETURN i {
                    .*,
                    createdAt: toString(i.createdAt)
                }
                ORDER BY rand()
                LIMIT 1
                """,
                user_id=user_id,
            ).single()
        )


def get_disagreeable_idea(driver, user_id):
    """
    Get an idea that the user is most likely to find interesting but wrong.
    1. Gets all idea nodes that are connected by three likes, but that are not directly connected to the user.
    2. For each path to each node, multiply together the degree of the likes for a
        crude score of agreement probability.
    3. For each node, add together the path scores.
    4. Return the node with the lowest value.
    """
    with driver.session() as session:
        result = session.execute_read(
            lambda tx: tx.run(
                """
                MATCH p = (u:User { userId: $user_id })-[:LIKES]->(:Idea)<-[:LIKES]-(:User)-[:LIKES]->(i:Idea)
                WHERE NOT (u)-[]->(i)
                WITH *, relationships(p) as likes
                WITH *, reduce(acc = 1, like IN likes | acc * like.agreement) AS agree
                RETURN i {
                    .*,
                    createdAt: toString(i.createdAt),
                    agreement: sum(agree)
                }
                ORDER BY i.agreement
                LIMIT 1
                """,
                user_id=user_id,
            ).single()
        )
        return result


def get_agreeable_idea(driver, user_id):
    """
    Get an idea that the user is most likely to find interesting and correct.
    Almost identical to get_disagreeable_idea.
    """
    with driver.session() as session:
        return session.execute_read(
            lambda tx: tx.run(
                """
                MATCH p = (u:User { userId: $user_id })-[:LIKES]->(:Idea)<-[:LIKES]-(:User)-[:LIKES]->(i:Idea)
                WHERE NOT (u)-[]->(i)
                WITH *, relationships(p) as likes
                WITH *, reduce(acc = 1, like IN likes | acc * like.agreement) AS agree
                RETURN i {
                    .*,
                    createdAt: toString(i.createdAt),
                    agreement: sum(agree)
                }
                ORDER BY i.agreement
                LIMIT 1
                """,
                user_id=user_id,
            ).single()
        )


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
            RETURN i.ideaId AS id, type(l) AS type, l.agreement AS agreement
            """,
            user_id=user_id,
            idea_id=idea_id,
            agreement=agreement,
        ).values("id", "type", "agreement")[0]
        return {"ideaId": result[0], "type": result[1], "agreement": result[2]}

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
            RETURN i.ideaId as id, d
            """,
            user_id=user_id,
            idea_id=idea_id,
        ).values("id", "d")[0]
        return {"ideaId": result[0], "type": result[1].type}

    with driver.session() as session:
        return session.execute_write(dislike, user_id, idea_id)


def delete_idea(driver, idea_id, user_id, admin=False) -> str | None:
    """Delete an idea"""

    def user_delete(tx, idea_id, user_id):
        result = tx.run(
            """
            MATCH (u:User {userId: $user_id})-[:POSTED]->(i:Idea {ideaId: $idea_id})
            WITH i, i.ideaId AS id
            DETACH DELETE i
            RETURN id
            """,
            idea_id=idea_id,
            user_id=user_id,
        ).single()
        return result.value("id")

    def admin_delete(tx, idea_id):
        result = tx.run(
            """
            MATCH (i:Idea {ideaId: $idea_id})
            WITH i, i.ideaId AS id
            DETACH DELETE i
            RETURN id
            """,
            idea_id=idea_id,
        ).single()
        return result.value("id")

    with driver.session() as session:
        if admin:
            return session.execute_write(admin_delete, idea_id)
        else:
            return session.execute_write(user_delete, idea_id, user_id)


def get_liked_ideas(driver, user_id: str) -> list:
    """Get all ideas that a user liked"""

    def user_liked(tx, user_id):
        result = tx.run(
            """
            MATCH (u:User {userId: $user_id})-[:LIKES]->(i:Idea)
            RETURN i
            """,
            user_id=user_id,
        ).value("i")
        return result

    with driver.session() as session:
        return session.execute_read(user_liked, user_id)


def get_disliked_ideas(driver, user_id: str) -> list:
    """Get all ideas that a user disliked"""

    def user_disliked(tx, user_id):
        result = tx.run(
            """
            MATCH (u:User {userId: $user_id})-[:DISLIKES]->(i:Idea)
            RETURN i
            """,
            user_id=user_id,
        ).value("i")
        return result

    with driver.session() as session:
        return session.execute_read(user_disliked, user_id)


def get_seen_ideas(driver, user_id: str) -> list:
    """Get all ideas that a user has a direct connection with"""

    def user_seen(tx, user_id):
        result = tx.run(
            """
            MATCH (u:User {userId: $user_id})-[]->(i:Idea)
            RETURN i {
                .*,
                createdAt: toString(i.createdAt)
            }
            """,
            user_id=user_id,
        ).value("i")
        return result

    with driver.session() as session:
        return session.execute_read(user_seen, user_id)


def get_all_seen_ideas_with_user_and_aggregate_reactions(driver, user_id: str) -> list:
    """Get all ideas that a user has a direct connection with, along with reaction data"""

    with driver.session() as session:
        return session.execute_read(
            lambda tx: tx.run(
                """
            MATCH (u:User {userId: $user_id})-[relationship:LIKES|DISLIKES]->(i:Idea)
            MATCH (:User)-[r:LIKES|DISLIKES]->(i)
            RETURN DISTINCT i {
                .*,
                createdAt: toString(i.createdAt),
                userAgreement: relationship.agreement,
                userRelationship: type(relationship),
                allReactions: collect(type(r)),
                allAgreement: collect(r.agreement)
            }
            """,
                user_id=user_id,
            ).value("i")
        )


def get_idea_details(
    driver, idea_id, with_reactions=False, user_id=None
) -> Idea | IdeaWithAnonReactions | IdeaWithAllReactions | None:
    """Get all details of an idea"""

    def with_no_reactions(tx, idea_id):
        result = tx.run(
            """
            MATCH (i:Idea {ideaId: $idea_id})
            RETURN i {
                .*,
                createdAt: toString(i.createdAt)
            }
            """,
            idea_id=idea_id,
        ).single()
        return result[0] if result else None

    def with_anon_reactions(tx, idea_id):
        result = tx.run(
            """
            MATCH (i:Idea {ideaId: $idea_id})
            OPTIONAL MATCH (:User)-[r:LIKES|DISLIKES]->(i)
            RETURN DISTINCT i {
                .*,
                createdAt: toString(i.createdAt),
                allReactions: collect(type(r)),
                allAgreement: collect(r.agreement)
            }
            """,
            idea_id=idea_id,
        ).single()
        return result[0] if result else None

    def with_all_reactions(tx, idea_id, user_id):
        result = tx.run(
            """
            MATCH (u:User {userId: $user_id})-[relationship:LIKES|DISLIKES]->(i:Idea {ideaId: $idea_id})
            OPTIONAL MATCH (:User)-[r]->(i:Idea {ideaId: $idea_id})
            RETURN DISTINCT i {
                .*,
                createdAt: toString(i.createdAt),
                userRelationship: type(relationship),
                userAgreement: relationship.agreement,
                allReactions: collect(type(r)),
                allAgreement: collect(r.agreement)
            }
            """,
            idea_id=idea_id,
            user_id=user_id,
        ).single()
        return result[0] if result else None

    with driver.session() as session:

        if user_id and with_reactions:
            return session.execute_read(with_all_reactions, idea_id, user_id)

        if with_reactions and user_id is None:
            return session.execute_read(with_anon_reactions, idea_id)

        return session.execute_read(with_no_reactions, idea_id)


def get_idea_with_reactions(driver, idea_id, user_id):
    """Get idea details along with user reaction"""

    with driver.session() as session:
        result = session.execute_read(
            lambda tx: tx.run(
                """
                MATCH (u:User {userId: $user_id})-[r]->(i:Idea {ideaId: $idea_id})
                RETURN i {
                    .*,
                    createdAt: toString(i.createdAt)
                }, r
                """,
                idea_id=idea_id,
                user_id=user_id,
            ).values("i", "r")[0]
        )
        return {**result[0], "reaction": (result[1].type, result[1]["agreement"])}


def get_idea_with_all_reactions(driver, idea_id):
    """Get idea details with anonymous reactions statistics"""

    with driver.session() as session:
        return session.execute_read(
            lambda tx: tx.run(
                """
                MATCH (:User)-[r]->(i:Idea {ideaId: $idea_id})
                RETURN DISTINCT i {
                    .*,
                    createdAt: toString(i.createdAt),
                    userAgreement: reaction.agreement,
                    userRelationship: type(reaction),
                    allReactions: collect(type(r)),
                    allAgreement: collect(r.agreement)
                }
                """,
                idea_id=idea_id,
            ).single()["i"]
        )


def get_posted_ideas(driver, user_id):
    """Get all ideas posted by a user"""

    with driver.session() as session:
        return session.execute_read(
            lambda tx: tx.run(
                """
                MATCH (u:User {userId: $user_id})-[:POSTED]->(i:Idea)
                MATCH (u)-[reaction:LIKES|DISLIKES]->(i)
                MATCH (:User)-[r:LIKES|DISLIKES]->(i)
                RETURN i {
                    .*,
                    createdAt: toString(i.createdAt),
                    userAgreement: reaction.agreement,
                    userRelationship: type(reaction),
                    allReactions: collect(type(r)),
                    allAgreement: collect(r.agreement)
                }
                """,
                user_id=user_id,
            ).value("i")
        )


##############################################################################
# Helper functions
#
