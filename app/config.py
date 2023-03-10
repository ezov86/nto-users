from configparser import ConfigParser


class Config:
    class _Alembic:
        db_url: str
        db_dev_url: str

    class _SQLAlchemy:
        db_url: str

    class _UserDefault:
        scopes: list

    class _Email:
        smtp_tls: bool
        smtp_host: str
        smtp_port: int
        smtp_user: str
        smtp_password: str
        smtp_from: str

        verify_url: str
        verify_token_expire: int
        verify_token_secret: str

        pwd_update_url: str
        pwd_update_token_expire: int
        pwd_update_token_secret: str

    class _OAuth:
        access_token_expire: int
        access_token_secret: str

        refresh_token_expire: int
        refresh_token_secret: str

    class _Telegram:
        token_secret: str

    def __init__(self):
        self.alembic = Config._Alembic()
        self.sqlalchemy = Config._SQLAlchemy()
        self.user_default = Config._UserDefault()
        self.email = Config._Email()
        self.oauth = Config._OAuth()
        self.telegram = Config._Telegram()

    def load_from_ini(self):
        parser = ConfigParser()

        parsed_files = parser.read(["../users.ini", "users.ini"])
        assert len(parsed_files) != 0

        parsed_sections = parser.sections()

        for section_name in self.__dict__.keys():
            assert section_name in parsed_sections, f"section '{section_name}' not found"
            parsed_section = parser[section_name]
            section = getattr(self, section_name)

            for key, type_ in section.__annotations__.items():
                assert key in parsed_section, f"value '{section_name}.{key}' not found"

                if type_ == list:
                    value = str(parsed_section[key]).split(",")
                else:
                    value = type_(parsed_section[key])

                setattr(section, key, value)


_config = Config()


def load_config():
    _config.load_from_ini()


def get_config() -> Config:
    return _config
