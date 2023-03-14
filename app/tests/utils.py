import random
import string
from copy import copy
from datetime import datetime, timedelta

from app.core.models import User, TelegramAccount


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


def tg_token_payload_from_data(data: dict) -> dict:
    # Replace "tg_user_id" with "sub".
    data["sub"] = data["tg_user_id"]
    del data["tg_user_id"]
    return data
