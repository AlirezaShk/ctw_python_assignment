from abc import ABC, abstractclassmethod
from faker.factory import Factory

Faker = Factory.create


class BaseFactory(ABC):
    fake = Faker()

    def __init__(self):
        self.fake.seed(hash(__file__))

    @abstractclassmethod
    def mock(cls) -> object: pass
