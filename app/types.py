from typing import TypedDict


class RegistrationData(TypedDict):
    email: str
    password: str
    username: str


class IdeaData(TypedDict):
    url: str
    user_id: str
    source_id: str | None
    description: str


class SourceData(TypedDict):
    name: str


class Idea(TypedDict):
    createdAt: str
    description: str
    url: str
    ideaId: str


class IdeaWithAnonReactions(TypedDict):
    createdAt: str
    description: str
    url: str
    ideaId: str
    allReactions: list[str]
    allAgreement: list[int]


class IdeaWithAllReactions(TypedDict):
    createdAt: str
    description: str
    url: str
    ideaId: str
    userReaction: str
    userAgreement: int
    allReactions: list[str]
    allAgreement: list[int]
