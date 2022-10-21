from typing import TypedDict


class RegistrationData(TypedDict):
    email: str
    password: str
    username: str


class IdeaData(TypedDict):
    url: str
    user_id: str
    source_id: str
    description: str


class SourceData(TypedDict):
    name: str
