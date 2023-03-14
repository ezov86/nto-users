import random

from faker import Faker
from faker.providers import BaseProvider

from app.core.models import User, TelegramAccount


class CommonProvider(BaseProvider):
    def none_or(self, v: any) -> any:
        return random.choice([v, None])

    def list_of(self, func, min_=2, max_=6) -> any:
        return [func() for _ in range(random.randint(min_, max_))]


class ModelsProvider(BaseProvider):
    def _apply_specified_fields(self, fields: dict, spec_fields: dict = None, ignore: list[str] = None):
        if spec_fields is None:
            spec_fields = {}

        if ignore is None:
            ignore = []

        for key, value in spec_fields:
            fields[key] = value

        return {k: v for k, v in fields.items() if k not in ignore}

    def user_data(self, **kwargs) -> dict:
        fields = {
            "name": self.generator.user_name(),
            "is_disabled": self.generator.pybool(),
            "scopes": self.generator.list_of(self.generator.word),
            "registered_at": self.generator.date_time()
        }

        return self._apply_specified_fields(fields, **kwargs)

    def user_model(self, **kwargs) -> User:
        return User(**self.user_data(**kwargs))

    def tg_account_data(self, **kwargs) -> dict:
        fields = {
            "tg_user_id": str(self.random_number()),
            "tg_username": self.generator.user_name(),
            "tg_first_name": self.generator.first_name(),
            "tg_last_name": self.generator.none_or(self.generator.last_name()),
            "tg_photo_url": self.generator.none_or(self.generator.image_url())
        }

        return self._apply_specified_fields(fields, **kwargs)

    def tg_account_model(self, **kwargs) -> TelegramAccount:
        return TelegramAccount(**self.tg_account_data(**kwargs))


def get_faker() -> Faker:
    fake = Faker()

    fake.add_provider(CommonProvider)
    fake.add_provider(ModelsProvider)

    return fake
