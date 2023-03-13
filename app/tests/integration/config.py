from starlette.testclient import TestClient

import app.config

_config = app.config.Config()


def override_config(client: TestClient):
    """
    Overriding get_config() dependency for use of set_config() by tests.

    If field is not set by set_config() then it is undefined.
    """

    def get_config():
        return _config

    client.app.dependency_overrides[app.config.get_config] = get_config


def reset_config():
    """
    Should be called at fixture teardown to reset config.
    """

    global _config

    _config = app.config.Config()


def set_config(**kwargs):
    """
    Should be called by fixture to set config vars.
    """
    for section_name, section_dic in kwargs.items():
        section = getattr(_config, section_name)
        for key, value in section_dic.items():
            setattr(section, key, value)
