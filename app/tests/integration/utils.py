import random
import string
from copy import copy
from datetime import datetime, timedelta

from dateutil.parser import parse
from sqlalchemy.orm import Session

from app.core.models import User, TelegramAuthData
from app.core.crypto import encode_jwt
from app.tests.integration.sync_db import get_sync_session


def datetime_soft_assert(result: datetime, expected: datetime):
    delta = abs(result - expected)
    assert delta < timedelta(seconds=2)


def _del_if_exists(dic: dict, key: str):
    if key in dic:
        del dic[key]


def _model_to_dic(model) -> dict:
    dic = copy(model.__dict__)
    _del_if_exists(dic, "id")
    _del_if_exists(dic, "_sa_instance_state")
    return dic


def assert_tg_auth_data(result: TelegramAuthData, expected: TelegramAuthData):
    res_dic = _model_to_dic(result)
    exp_dic = _model_to_dic(expected)

    assert res_dic == exp_dic


def assert_user(result: User, expected: User):
    res_dic = _model_to_dic(result)
    exp_dic = _model_to_dic(expected)

    datetime_soft_assert(result.registered_at, result.registered_at)

    _del_if_exists(res_dic, "telegram_auth")
    _del_if_exists(exp_dic, "telegram_auth")

    del res_dic["registered_at"]
    del exp_dic["registered_at"]

    assert res_dic == exp_dic


def assert_user_json(result: dict, expected: dict):
    datetime_soft_assert(parse(result["registered_at"]), parse(expected["registered_at"]))

    del result["id"]
    del result["registered_at"]
    del expected["registered_at"]

    assert result == expected


def assert_all_models(model, assert_func, expected: list):
    session = get_sync_session()

    models_in_db = session.query(model).all()
    assert len(models_in_db) == len(expected)

    for model_in_db, expected_model in zip(models_in_db, expected):
        assert_func(model_in_db, expected_model)


def assert_all_users(expected: list[User]):
    assert_all_models(User, assert_user, expected)


def assert_all_tg_auth_data(expected: list[TelegramAuthData]):
    assert_all_models(TelegramAuthData, assert_tg_auth_data, expected)


def rand_str() -> str:
    return "".join(random.choices(
        string.ascii_uppercase + string.digits + string.ascii_lowercase,
        k=20
    ))


def get_stub_user(name: str = None, is_disabled: bool = False, scopes: list[str] = None) -> User:
    if name is None:
        name = rand_str()

    if scopes is None:
        scopes = ["scope1", "scope2"]

    return User(
        name=name,
        is_disabled=is_disabled,
        scopes=scopes,
        registered_at=datetime.utcnow()
    )


def with_session(func, *args, **kwargs) -> any:
    session = get_sync_session()
    return func(session, *args, **kwargs)


def create_model(session: Session, model) -> any:
    session.add(model)
    session.commit()
    session.refresh(model)
    return model


def update_model(session: Session, model) -> any:
    session.commit()
    session.refresh(model)
    return model


def get_by_id(session, model_type, id_: int) -> any:
    return session.get(model_type, id_)


def encode_access_token(username: str, scopes: str) -> str:
    return encode_jwt(username, "access_token_secret", 1, extra_payload={"scopes": scopes})


def update_scopes(session: Session, user: User, scopes: list[str]):
    user_from_db = get_by_id(session, User, user.id)
    user_from_db.scopes = scopes
    update_model(session, user_from_db)
    return user_from_db
