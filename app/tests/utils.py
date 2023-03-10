import random
import string
from datetime import datetime, timedelta

from dateutil.parser import parse

from app.core.models import User, TelegramAuthEntry
from .db import get_session


def datetime_soft_assert(result: datetime, expected: datetime):
    delta = abs(result - expected)
    assert delta < timedelta(seconds=2)


def del_if_exists(dic: dict, key: str):
    if key in dic:
        del dic[key]


def _assert_model_dict(result, expected, fields_to_remove: list[str]):
    for key in fields_to_remove + ["id", "_sa_instance_state"]:
        del_if_exists(result, key)
        del_if_exists(expected, key)

    assert result == expected


def assert_user_dict(result: dict, expected: dict):
    datetime_soft_assert(
        parse(result["registered_at"]),
        parse(expected["registered_at"])
    )
    _assert_model_dict(
        result,
        expected,
        ["registered_at"]
    )


def assert_user_model(result: User, expected: User):
    datetime_soft_assert(result.registered_at, expected.registered_at)
    _assert_model_dict(
        result.__dict__,
        expected.__dict__,
        ["registered_at"]
    )


def assert_tg_auth_entry(result: TelegramAuthEntry, expected: TelegramAuthEntry):
    _assert_model_dict(
        result.__dict__,
        expected.__dict__,
        ["user"]
    )


def _assert_all_models(model, assert_func, expected: list):
    session = next(get_session())

    models_in_db = session.query(model).all()
    assert len(models_in_db) == len(expected)

    for model_in_db, expected_model in zip(models_in_db, expected):
        assert_func(model_in_db, expected_model)


def assert_all_users(expected: list[User]):
    _assert_all_models(User, assert_user_model, expected)


def assert_all_tg_auth_entries(expected: list[TelegramAuthEntry]):
    _assert_all_models(TelegramAuthEntry, assert_tg_auth_entry, expected)


def rand_str() -> str:
    return "".join(random.choices(
        string.ascii_uppercase + string.digits + string.ascii_lowercase,
        k=20
    ))


def get_stub_user() -> User:
    return User(
        name=rand_str(),
        is_disabled=False,
        scopes=["scope1", "scope2"],
        registered_at=datetime.utcnow()
    )


def create_model(model) -> any:
    session = next(get_session())
    session.add(model)
    session.commit()
    session.refresh(model)
    return model
