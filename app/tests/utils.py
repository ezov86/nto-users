import random
import string
from copy import copy
from datetime import datetime, timedelta

from app.core.models import User


def rand_str() -> str:
    return "".join(random.choices(
        string.ascii_uppercase + string.digits + string.ascii_lowercase,
        k=20
    ))


def datetime_soft_assert(result: datetime, expected: datetime):
    delta = abs(result - expected)
    assert delta < timedelta(seconds=2)


def assert_model_eq(result, expected):

    res_dic = copy(result.__dict__)
    exp_dic = copy(expected.__dict__)

    del exp_dic["_sa_instance_state"]

    for field in res_dic.keys():
        if field not in exp_dic:
            del res_dic[field]

    assert res_dic == exp_dic


def assert_user_eq(result: User, expected: User):
    datetime_soft_assert(result.registered_at, expected.registered_at)

    assert_model_eq(result, expected)
