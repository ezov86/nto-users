import random
from datetime import datetime

import pytest
from starlette.testclient import TestClient

from .config import set_config
from .utils import assert_all_users, create_model, rand_str, encode_access_token, update_scopes, with_session, \
    get_stub_user, assert_user_json, assert_all_tg_auth_data

from app.core.crypto import encode_jwt
from app.core.models import User, TelegramAuthData


@pytest.fixture(autouse=True)
def tg_config():
    set_config(
        telegram={
            "token_secret": "telegram_token_secret",
        },
        user_default={
            "scopes": ["scope1", "scope2"]
        }
    )


@pytest.fixture()
def tg_profile_data() -> dict:
    return {
        "tg_username": rand_str(),
        "tg_first_name": rand_str(),
        "tg_last_name": random.choice([rand_str(), None]),
        "tg_photo_url": random.choice([rand_str(), None])
    }


def encode_tg_token(tg_user_id: str, profile_data: dict) -> str:
    return encode_jwt(tg_user_id, "telegram_token_secret", 10000, extra_payload=profile_data)


@pytest.fixture(scope="module")
def tg_token(rand_tg_user_id: str) -> str:
    return encode_jwt(rand_tg_user_id, "telegram_token_secret")


@pytest.fixture()
def user_with_tg_auth(
        rand_tg_user_id: str,
        stub_user: User
) -> tuple[TelegramAuthData, User]:
    tg_auth_entry = with_session(create_model, TelegramAuthData(
        tg_user_id=rand_tg_user_id,
        user_id=stub_user.id
    ))
    return tg_auth_entry, stub_user


@pytest.fixture()
def disabled_user_with_tg_auth(
        rand_tg_user_id: str,
        stub_disabled_user: User
) -> tuple[TelegramAuthData, User]:
    tg_auth_entry = with_session(create_model, TelegramAuthData(
        tg_user_id=rand_tg_user_id,
        user_id=stub_disabled_user.id
    ))
    return tg_auth_entry, stub_disabled_user


def test_tg_register(
        client: TestClient,
        tg_profile_data: dict
):
    username = rand_str()
    tg_user_id = rand_str()
    tg_token = encode_tg_token(tg_user_id, tg_profile_data)

    resp = client.post(
        url="/tg/register",
        json={
            "name": username,
            "token": tg_token
        }
    )

    assert resp.status_code == 201

    assert_user_json(resp.json(), {
        "name": username,
        "is_disabled": False,
        "scopes": ["scope1", "scope2"],
        "registered_at": str(datetime.utcnow())
    })

    assert_all_users([User(
        name=username,
        is_disabled=False,
        scopes=["scope1", "scope2"],
        registered_at=datetime.utcnow()
    )])

    assert_all_tg_auth_data([TelegramAuthData(
        tg_user_id=tg_user_id,
        **tg_profile_data,
        user_id=resp.json()["id"]
    )])


def test_tg_register_with_invalid_token(
        client: TestClient,
        read_only
):
    resp = client.post(
        url="/tg/register",
        json={
            "name": "user",
            "token": "not a valid token"
        }
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "Invalid authentication data"
    }


def test_tg_register_existing_user(
        client: TestClient,
        stub_user: User,
        read_only
):
    resp = client.post(
        url="/tg/register",
        json={
            "name": stub_user.name,
            "token": encode_tg_token(rand_str())
        }
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "User already exists"
    }


def test_tg_register_existing_tg_user(
        client: TestClient,
        user_with_tg_auth: User,
        tg_token: str,
        read_only
):
    resp = client.post(
        url="/tg/register",
        json={
            "name": user_with_tg_auth.name,
            "token": encode_tg_token(user_with_tg_auth.telegram_auth.tg_user_id)
        }
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "User already exists"
    }


def test_tg_login(
        client: TestClient,
        user_with_tg_auth: User,
        oauth_config
):
    resp = client.post(
        url="/tg/login",
        json={
            "scope": "scope1 scope2 admin",
            "token": encode_tg_token(user_with_tg_auth.telegram_auth.tg_user_id)
        }
    )

    assert resp.status_code == 200

    access, refresh = resp.json()["access"], resp.json()["refresh"]

    # Check access token is ok.
    resp = client.get(
        url="/tokens/user",
        headers=[("Authorization", "Bearer " + access)]
    )

    assert resp.status_code == 200
    assert resp.json() == {
        "name": user_with_tg_auth.name,
        "scopes": ["scope1", "scope2"]
    }

    # Check refresh token is ok.
    resp = client.post(
        url="/tokens/refresh",
        headers=[("Refresh-Token", refresh)]
    )

    assert resp.status_code == 200


def test_tg_login_with_invalid_token(
        client: TestClient,
        user_with_tg_auth: User,
        oauth_config,
        read_only
):
    resp = client.post(
        url="/tg/login",
        json={
            "scope": "scope1 scope2",
            "token": "not a valid token"
        }
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "Invalid authentication data"
    }


def test_tg_login_disabled_user(
        client: TestClient,
        disabled_user_with_tg_auth: User,
        oauth_config,
        read_only
):
    tg_auth = disabled_user_with_tg_auth.telegram_auth
    resp = client.post(
        url="/tg/login",
        json={
            "scope": "scope1 scope2",
            "token": encode_tg_token(tg_auth.tg_user_id)
        }
    )

    assert resp.status_code == 403
    assert resp.json() == {
        "detail": "User is not permitted"
    }


def test_tg_add_to_user(
        client: TestClient,
        stub_user: User,
        rand_tg_user_id: str,
        tg_token: str,
        oauth_config
):
    access_token = encode_access_token(stub_user.name, "users:tg:add")
    stub_user = with_session(update_scopes, stub_user, ["users:tg:add"])

    resp = client.post(
        url="/tg/add",
        headers=[("Authorization", "Bearer " + access_token)],
        json={
            "token": tg_token
        }
    )

    assert resp.status_code == 204

    assert_all_users([stub_user])

    assert_all_tg_auth_data([TelegramAuthData(
        tg_user_id=rand_tg_user_id,
        user_id=stub_user.id
    )])


def test_tg_add_to_user_with_invalid_scopes(
        client: TestClient,
        stub_user: User,
        tg_token: str,
        oauth_config,
        read_only
):
    access_token = encode_access_token(stub_user.name, "")

    resp = client.post(
        url="/tg/add",
        headers=[("Authorization", "Bearer " + access_token)],
        json={
            "token": tg_token
        }
    )

    assert resp.status_code == 403
    assert resp.json() == {
        "detail": "User is not permitted"
    }


def test_tg_add_already_attached(
        client: TestClient,
        user_with_tg_auth,
        tg_token: str,
        oauth_config,
        read_only
):
    access_token = encode_access_token(user_with_tg_auth[1].name, "users:tg:add")
    with_session(update_scopes, user_with_tg_auth[1], ["users:tg:add"])

    resp = client.post(
        url="/tg/add",
        headers=[("Authorization", "Bearer " + access_token)],
        json={
            "token": tg_token
        }
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "Telegram user already attached"
    }


def test_tg_add_already_attached_to_another_user(
        client: TestClient,
        user_with_tg_auth,
        tg_token: str,
        oauth_config,
        read_only
):
    # Create another stub user without Telegram auth.
    stub_user2 = with_session(create_model, get_stub_user(scopes=["users:tg:add"]))

    access_token = encode_access_token(stub_user2.name, "users:tg:add")

    resp = client.post(
        url="/tg/add",
        headers=[("Authorization", "Bearer " + access_token)],
        json={
            "token": tg_token
        }
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "Telegram user already attached"
    }
