from sqlalchemy import event
from sqlalchemy.orm import Session

from app.config import Config
from app.db import connect_to_db
from app.tests.integration.config import set_config, reset_config

_readonly = False


def set_db_readonly(value: bool):
    """
    Set readonly mode for async SQLAlchemy session.
    """
    global _readonly
    _readonly = value


def configure_test_sqlalchemy_async_db(real_config: Config):
    # Replace async DB URL with the test one.
    set_config(
        sqlalchemy={"async_db_url": real_config.tests.async_db_url}
    )

    # Connect SQLAlchemy to test DB.
    connect_to_db()

    reset_config()

    # For readonly mode:
    @event.listens_for(Session, "after_flush")
    def after_flush(session, flush_context):
        if _readonly:
            raise AssertionError("Flush occurred in DB readonly mode")
