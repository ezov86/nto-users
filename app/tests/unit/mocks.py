from app.config import Config


def get_mock_config(**kwargs):
    """
    Put sections dicts into kwargs.
    """
    config = Config()
    for section_name, section_dic in kwargs.items():
        section = getattr(config, section_name)
        for key, value in section_dic.items():
            setattr(section, key, value)

    return config
