import asyncio
import random
import string
from copy import copy
from datetime import datetime, timedelta

from app.core.models import User, TelegramAccount


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper


def rand_str() -> str:
    return "".join(random.choices(
        string.ascii_uppercase + string.digits + string.ascii_lowercase,
        k=20
    ))


def rand_str_or_none() -> str | None: return random.choices([rand_str(), None])[0]


def rand_bool() -> bool: return random.choices([True, False])


def rand_datetime(range_: tuple[datetime, datetime] = None) -> datetime:
    if range_ is None:
        range_ = datetime(2000, 1, 1), datetime.utcnow()

    start, end = range_
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


def rand_user(**specified_fields) -> User:
    """
    Get user with random data. Email/Telegram accounts omitted.

    :param specified_fields: values for fields. If no value for field given, random generated.
    """

    fields = {
        "name": rand_str(),
        "is_disabled": rand_bool(),
        "scopes": [rand_str() for _ in range(random.randint(2, 6))],
        "registered_at": rand_datetime()
    }

    for key, value in specified_fields:
        fields[key] = value

    return User(**fields)


def datetime_soft_assert(result: datetime, expected: datetime):
    delta = abs(result - expected)
    assert delta < timedelta(seconds=2)


def assert_model_eq(result, expected):
    exp_dic = copy(expected.__dict__)
    del exp_dic["_sa_instance_state"]

    # Remove all fields that are not specified in 'expected' object.
    res_dic = {k: v for k, v in copy(result.__dict__).items() if k in exp_dic}

    assert res_dic == exp_dic


def assert_user_eq(result: User, expected: User):
    datetime_soft_assert(result.registered_at, expected.registered_at)

    assert_model_eq(result, expected)


def assert_tg_account_eq(result: TelegramAccount, expected: TelegramAccount):
    assert_model_eq(result, expected)
