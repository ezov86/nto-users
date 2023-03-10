from datetime import datetime

import pytest
from starlette.testclient import TestClient

from .config import set_config
from .utils import assert_all_users, assert_all_tg_auth_entries, assert_user_dict, create_model, rand_str

from app.core.crypto import encode_jwt
from app.core.models import User, TelegramAuthEntry

TG_SECRET = "tg_secret"
TG_SCOPES = ["scope1", "scope2"]


@pytest.fixture(scope="module")
def rand_tg_user_id() -> str:
    return rand_str()


@pytest.fixture(autouse=True)
def tg_config():
    set_config(
        telegram={
            "token_secret": TG_SECRET,
        },
        user_default={
            "scopes": TG_SCOPES
        }
    )


def encode_tg_token(tg_user_id: str) -> str:
    return encode_jwt(tg_user_id, TG_SECRET)


@pytest.fixture(scope="module")
def tg_token(rand_tg_user_id: str) -> str:
    return encode_jwt(rand_tg_user_id, TG_SECRET)


@pytest.fixture()
def stub_tg_auth(
        rand_tg_user_id: str,
        stub_user: User
) -> tuple[TelegramAuthEntry, User]:
    tg_auth_entry = create_model(TelegramAuthEntry(
        tg_user_id=rand_tg_user_id,
        user_id=stub_user.id
    ))

    return tg_auth_entry, stub_user


def test_tg_register(
        client: TestClient,
        tg_token: str,
        rand_username: str,
        rand_tg_user_id: str
):
    resp = client.post(
        url="/tg/register",
        json={
            "name": rand_username,
            "token": tg_token
        }
    )

    assert_user_dict(resp.json(), {
        "name": rand_username,
        "is_disabled": False,
        "scopes": TG_SCOPES,
        "registered_at": str(datetime.utcnow())
    })

    assert resp.status_code == 201

    assert_all_users([User(
        name=rand_username,
        is_disabled=False,
        scopes=TG_SCOPES,
        registered_at=datetime.utcnow()
    )])

    assert_all_tg_auth_entries([TelegramAuthEntry(
        tg_user_id=rand_tg_user_id,
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
        tg_token,
        read_only
):
    resp = client.post(
        url="/tg/register",
        json={
            "name": stub_user.name,
            "token": tg_token
        }
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "User already exists"
    }


def test_tg_register_existing_tg_user(
        client: TestClient,
        stub_tg_auth: tuple[TelegramAuthEntry, User],
        tg_token: str,
        rand_username: str,
        read_only
):
    resp = client.post(
        url="/tg/register",
        json={
            "name": rand_username,
            "token": tg_token
        }
    )

    assert resp.status_code == 400
    assert resp.json() == {
        "detail": "User already exists"
    }


def test_tg_login(
        client: TestClient,
        stub_tg_auth: tuple[TelegramAuthEntry, User],
        oauth_config
):
    resp = client.post(
        url="/tg/login",
        json={
            "scope": "scope1 scope2",
            "token": encode_tg_token(stub_tg_auth[0].tg_user_id)
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
        "name": stub_tg_auth[1].name,
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
        stub_tg_auth: tuple[TelegramAuthEntry, User],
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


def test_tg_login_with_not_permitted_scope(
        client: TestClient,
        stub_tg_auth: tuple[TelegramAuthEntry, User],
        oauth_config,
        read_only
):
    resp = client.post(
        url="/tg/login",
        json={
            "scope": "admin scope1",
            "token": encode_tg_token(stub_tg_auth[0].tg_user_id)
        }
    )

    assert resp.status_code == 403
    assert resp.json() == {
        "detail": "User is not permitted"
    }
