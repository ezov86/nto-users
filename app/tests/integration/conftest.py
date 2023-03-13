import pytest
from starlette.testclient import TestClient

from app.config import load_config, get_config
from app.core.models import User
from app.main import app
from app.tests.integration.async_db import configure_test_sqlalchemy_async_db, set_db_readonly
from app.tests.integration.config import override_config, reset_config, set_config
from app.tests.integration.sync_db import truncate_tables, init_sync_db
from app.tests.integration.utils import create_model, get_stub_user, with_session


@pytest.fixture(scope="session")
def client() -> TestClient:
    client = TestClient(app)

    # Load config from 'users.ini' for [tests] section.
    load_config()
    real_config = get_config()

    override_config(client)

    configure_test_sqlalchemy_async_db(real_config)
    init_sync_db(real_config)

    return client


@pytest.fixture(autouse=True)
def db_cleanup():
    yield
    truncate_tables()


@pytest.fixture()
def read_only():
    set_db_readonly(True)
    yield
    set_db_readonly(False)


@pytest.fixture(autouse=True)
def config_cleanup():
    yield
    reset_config()


@pytest.fixture()
def stub_user() -> User:
    return with_session(create_model, get_stub_user())


@pytest.fixture()
def stub_disabled_user() -> User:
    return with_session(create_model, get_stub_user(is_disabled=True))


@pytest.fixture()
def oauth_config():
    set_config(oauth={
        "access_token_expire": 1,
        "access_token_secret": "access_token_secret",

        "refresh_token_expire": 1,
        "refresh_token_secret": "refresh_token_secret"
    })
