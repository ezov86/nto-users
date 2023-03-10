import pytest
from starlette.testclient import TestClient

from app.core.models import User
from app.main import app
from app.tests.config import override_config, reset_config, set_config
from app.tests.db import override_db, finalize_overriden_db, ignore_db_readonly, truncate_tables, db_set_readonly_mode
from app.tests.utils import rand_str, create_model, get_stub_user


@pytest.fixture(scope="session")
def client() -> TestClient:
    client = TestClient(app)

    override_db(client)
    override_config(client)

    yield client

    finalize_overriden_db()


@pytest.fixture(autouse=True)
def db_cleanup():
    yield
    with ignore_db_readonly():
        truncate_tables()


@pytest.fixture()
def read_only():
    db_set_readonly_mode(True)
    yield
    db_set_readonly_mode(False)


@pytest.fixture(autouse=True)
def config_cleanup():
    yield
    reset_config()


@pytest.fixture()
def rand_username() -> str:
    return rand_str()


@pytest.fixture()
def stub_user() -> User:
    with ignore_db_readonly():
        return create_model(get_stub_user())


@pytest.fixture()
def oauth_config():
    set_config(oauth={
        "access_token_expire": 1,
        "access_token_secret": "access_token_secret",

        "refresh_token_expire": 1,
        "refresh_token_secret": "refresh_token_secret"
    })
