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
    postedBy: str


class IdeaWithScore(TypedDict):
    createdAt: str
    score: float
    popularity: int
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
    postedBy: str


class IdeaWithAllReactions(TypedDict):
    createdAt: str
    description: str
    url: str
    ideaId: str
    userReaction: str
    userAgreement: int
    allReactions: list[str]
    allAgreement: list[int]
    postedBy: str


class User(TypedDict):
    userId: str
    email: str
    username: str
    password: str


class UserData(TypedDict):
    userId: str
    email: str
    username: str


class UserToken(TypedDict):
    userId: str
    email: str
    username: str
    sub: str
    iat: str
    nbf: str
    exp: str
    token: str
