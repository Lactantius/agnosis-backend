from faker import Faker

from app.types import RegistrationData

fake = Faker()
Faker.seed(0)


def fake_user(_) -> RegistrationData:
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
    }


def fake_source(_):
    return {"name": fake.name()}


def fake_idea(_):
    return {"url": fake.url(), "description": fake.text()}


users = list(map(fake_user, range(10)))

sources = list(map(fake_source, range(10)))

ideas = list(map(fake_idea, range(10)))
